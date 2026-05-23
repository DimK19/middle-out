import os
import tempfile
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image
from pillow_heif import register_heif_opener
import concurrent.futures

# Import your custom modules
from metrics_per_channel import evaluate_ycbcr
from vmaf import get_image_vmaf
from histogram_parallel import save_original_histogram, save_compressed_histogram
from difference_map import save_diff_maps

# Ensure HEIF opener is registered (important for Windows multi-processing)
register_heif_opener()

def save_ssim_maps(ssim_maps, output_dir):
    """Saves SSIM maps as PNGs and closes the plot to prevent RAM leaks."""
    plt.style.use('default')
    os.makedirs(output_dir, exist_ok=True)
    
    for ch, maps_by_window in ssim_maps.items():
        for w, m in maps_by_window.items():
            fig = plt.figure()
            plt.title(f"SSIM Map - {ch} (Window Size: {w})")
            plt.imshow(m, cmap='gray', vmin=0, vmax=1) 
            plt.colorbar()
            
            filepath = os.path.join(output_dir, f"SSIM_Map_{ch}_w{w}.png")
            plt.savefig(filepath, bbox_inches='tight', dpi=200) 
            plt.close(fig)

# --- WORKER FUNCTION FOR PARALLELIZATION ---
def process_single_case(item, png_size_bytes, max_y_scale, output_base_dir):
    """This function processes a single compressed image and runs in a separate process."""
    # Re-register for Windows 'spawn' compatibility in child processes
    register_heif_opener() 
    
    orig_path = item["original"]
    comp_path = item["compressed"]
    img_format = item["format"]
    qual_level = item["level"]
    orig_basename = os.path.splitext(os.path.basename(orig_path))[0]
    
    # --- 1. Size calculations ---
    comp_size_bytes = os.path.getsize(comp_path)
    storage_saved_pct = (1 - (comp_size_bytes / png_size_bytes)) * 100

    # --- 2. Run Evaluations ---
    result = evaluate_ycbcr(orig_path, comp_path, window_sizes=(7, 11, 21))
    per_channel = result.get('per_channel', result)
    maps = result.get('ssim_maps', {})

    vmaf_score = get_image_vmaf(comp_path, orig_path)
    
    # --- 3. Save Diagrams & Histograms ---
    diagram_dir = os.path.join(output_base_dir, "images", orig_basename, f"{img_format}_{qual_level}")
    os.makedirs(diagram_dir, exist_ok=True)
    
    if maps:
        save_ssim_maps(maps, diagram_dir)
        # Process ONLY the compressed histogram using the fixed scale
        save_compressed_histogram(comp_path, diagram_dir, max_y_scale) 
        save_diff_maps(orig_path, comp_path, diagram_dir)

    # --- 4. Collate Numeric Data ---
    row_data = {
        "Original_Image": orig_basename,
        "Format": img_format,
        "Quality_Level": qual_level,
        "VMAF": vmaf_score,
        "Compressed_Size_Bytes": comp_size_bytes,
        "Baseline_PNG_Bytes": png_size_bytes,
        "Storage_Saved_%": round(storage_saved_pct, 2)
    }

    # Dynamically unpack Y, Cb, Cr metrics
    for channel, metrics in per_channel.items():
        row_data[f"{channel}_MSE"] = metrics.get("mse")
        row_data[f"{channel}_PSNR"] = metrics.get("psnr")
        
        ssim_dict = metrics.get("ssim", {})
        for w, ssim_val in ssim_dict.items():
            row_data[f"{channel}_SSIM_w{w}"] = ssim_val

    return row_data


# --- MAIN PIPELINE RUNNER ---
def run_evaluation_pipeline(test_cases, output_base_dir="pipeline_parallel_results"):
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 1. Extract unique original images to process them once
    unique_originals = list(set([item["original"] for item in test_cases]))
    baseline_data = {} # Will store {orig_path: {'size': bytes, 'max_y': float}}

    print("--- Phase 1: Pre-processing Original TIFs ---")
    for orig_path in unique_originals:
        orig_basename = os.path.splitext(os.path.basename(orig_path))[0]
        print(f"Processing baseline for: {orig_basename}")
        
        # Calculate Baseline PNG Size
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_png:
            Image.open(orig_path).save(temp_png, format="PNG")
            png_size = temp_png.tell()
            
        # Create a dedicated directory for the original's diagrams
        orig_diagram_dir = os.path.join(output_base_dir, "images", orig_basename, "TIFF")
        os.makedirs(orig_diagram_dir, exist_ok=True)
        
        # Save original histogram and get the max Y limit for this specific image
        max_y = save_original_histogram(orig_path, orig_diagram_dir)
        
        baseline_data[orig_path] = {'size': png_size, 'max_y': max_y}


    print("\n--- Phase 2: Parallelizing Compressed Images ---")
    all_metrics_data = []
    
    # Use ProcessPoolExecutor to map jobs to available CPU cores
    # (CPUs bound image processing works best with Processes, not Threads)
    with concurrent.futures.ProcessPoolExecutor(max_workers = 6) as executor:
        future_to_case = {}
        
        for item in test_cases:
            orig_path = item["original"]
            png_size = baseline_data[orig_path]['size']
            max_y = baseline_data[orig_path]['max_y']
            
            # Submit job to the pool
            future = executor.submit(
                process_single_case, 
                item, 
                png_size, 
                max_y, 
                output_base_dir
            )
            future_to_case[future] = item
            
        # As jobs finish, collect the results
        for future in concurrent.futures.as_completed(future_to_case):
            item = future_to_case[future]
            try:
                row_data = future.result()
                all_metrics_data.append(row_data)
                print(f"Completed: {item['original']} -> {item['format']} (Level {item['level']})")
            except Exception as exc:
                print(f"Error processing {item['original']} to {item['format']}: {exc}")

    # --- Phase 3: Export to CSV ---
    print("\n--- Phase 3: Aggregating Results ---")
    df_metrics = pd.DataFrame(all_metrics_data)
    csv_path = os.path.join(output_base_dir, "unified_results.csv")
    
    try:
        df_times = pd.read_csv("encoding_results\\encoding_times.csv")
        df_final = pd.merge(
            df_times, 
            df_metrics, 
            on=["Original_Image", "Format", "Quality_Level"], 
            how="outer" 
        )
        df_final.to_csv(csv_path, index=False)
        print(f"\nPipeline complete! Successfully merged with encoding times and saved to {csv_path}")
        
    except FileNotFoundError:
        print("\nWarning: 'encoding_times.csv' not found. Saving metrics without encoding times.")
        df_metrics.to_csv(csv_path, index=False)
        print(f"Pipeline complete! Results saved to {csv_path}")


if(__name__ == "__main__"):
    IMG_PATH = 'encoding_results\\compressed_images'
    testCases = []
    
    for i in os.listdir(IMG_PATH):
        orig, ext = i.split('.')
        if(orig[0:3] == 'DOC'):
            continue
        orig, level = orig.split('_')
        level = int(level)
        fmt = ext.upper() if ext != 'jpg' else 'JPEG'
        testCases.append({
            'original': f'originals\\{orig}.tif',
            'compressed': f'{IMG_PATH}\\{i}',
            'format': fmt,
            'level': level
        })
        
    run_evaluation_pipeline(testCases)