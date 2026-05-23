import os
from time import perf_counter
from PIL import Image
from pillow_heif import register_heif_opener
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

# Disable "decompression bomb" check
Image.MAX_IMAGE_PIXELS = None

# Register Pillow to understand HEIF/AVIF
register_heif_opener()

def process_single_image(input_file):
    print(f'Processing {input_file}')
    baseName = os.path.splitext(os.path.basename(input_file))[0]
    
    out_dir = os.path.join('encoding_results', 'compressed_images')
    os.makedirs(out_dir, exist_ok=True)
    
    encoding_results = []
    
    # Define the two extremes for quality
    # 1 = Lowest possible quality (0), 3 = Highest possible quality (100)
    quality_levels = {
        1: 1
    }
    
    # List of formats to process: (File Extension, Pillow Format Name)
    formats = [
        ("heic", "HEIF"),
        ("avif", "AVIF"),
        ("webp", "WEBP")
    ]
    
    try:
        # Open and load image into memory once
        with Image.open(input_file) as img:
            # CROPPING FIX
            w, h = img.size
            if w % 2 != 0 or h % 2 != 0:
                img = img.crop((0, 0, w - (w % 2), h - (h % 2)))
                # Overwrite
                img.save(input_file)

            mem_img = img.convert("RGB")
            
        for level, q_val in quality_levels.items():
            for ext, fmt_name in formats:
                out_path = os.path.join(out_dir, f"{baseName}_{level}.{ext}")
                
                start_time = perf_counter()
                
                # Directly compress with the specific quality value
                mem_img.save(out_path, format=fmt_name, quality=q_val)
                
                end_time = perf_counter()
                
                encoding_results.append({
                    "Original_Image": baseName,
                    "Format": fmt_name,
                    "Quality_Level": level,
                    "Encoding_Time_sec": end_time - start_time
                })
                
    except Exception as e:
        print(f"Error processing '{input_file}': {e}")
        
    print(f'Finished processing {input_file}')
    return encoding_results

# ==========================================
# Example Pipeline Execution
# ==========================================

if __name__ == "__main__":
    
    input_dir = 'documents'
    
    # Grab all valid files in the directory
    files_to_process = [
        os.path.join(input_dir, f) 
        for f in os.listdir(input_dir) 
        if os.path.isfile(os.path.join(input_dir, f))
    ]
    
    all_encoding_results = []
    
    print(f"Starting parallel batch processing for {len(files_to_process)} images...")

    with ProcessPoolExecutor(max_workers=4) as executor:
        # Schedule all files
        futures = {executor.submit(process_single_image, file): file for file in files_to_process}
        
        # Gather results as they complete
        for future in as_completed(futures):
            all_encoding_results.extend(future.result())

    # Save the consolidated CSV
    os.makedirs("encoding_results", exist_ok=True)
    df_times = pd.DataFrame(all_encoding_results)
    
    csv_path = os.path.join("encoding_results", "encoding_times.csv")
    df_times.to_csv(
        csv_path, 
        index=False, 
        mode='a',
        header=not os.path.exists(csv_path)
    )
    
    print(f"\nAll encoding complete! Saved combined {csv_path}.")