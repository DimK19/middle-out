import io
import os
import warnings
from time import perf_counter
from PIL import Image
from pillow_heif import register_heif_opener
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

## Disable "decompression bomb" check
Image.MAX_IMAGE_PIXELS = None

# Silence the metadata warning from the TIFF plugin
warnings.filterwarnings("ignore", category=UserWarning, module="PIL.TiffImagePlugin")

# Register Pillow to understand HEIF
register_heif_opener()

def encode_to_target_bpp(input_tiff, output_path, format_name, target_bpp, **kwargs):
    """
    Compresses an image to a target Bits Per Pixel (bpp) using a binary search.
    """
    # 1. Open the file and immediately create a purely memory-backed copy
    with Image.open(input_tiff) as img:
        # .convert("RGB") forces all pixel data into RAM and strips all file-pointer 
        # dependent metadata (like EXIF) completely. 
        mem_img = img.convert("RGB")
        
    # The 'with' block is now closed. The original TIFF file is closed.
    # We will use 'mem_img' for everything else. No more "closed file" errors!
    
    width, height = mem_img.width, mem_img.height
    
    # Calculate target file size in bytes
    ## target_bytes = (width * height * target_bpp) / 8
    original_size = os.path.getsize(input_tiff)
    if(target_bpp == 1.5):
        target_bytes = original_size / 16
    elif(target_bpp == 0.57):
        target_bytes = original_size / 42
    elif(target_bpp == 0.25):
        target_bytes = original_size / 96
    
    min_q = 0
    max_q = 100
    best_q = 50
    closest_diff = float('inf')
    best_image_bytes = None
    encoding_time = 0.0

    print(f"Searching for {format_name} at ~{target_bpp} bpp (Target: {int(target_bytes)} bytes)...")

    # 10 iterations is enough to binary search a 0-100 range
    for _ in range(10):
        q = (min_q + max_q) // 2
        buffer = io.BytesIO()
        
        start_time = perf_counter()
        # Save from our memory-backed image
        mem_img.save(buffer, format=format_name, quality=q, **kwargs)
        end_time = perf_counter()
        
        size = buffer.tell()
        diff = abs(size - target_bytes)
        
        if(diff < closest_diff):
            closest_diff = diff
            best_q = q
            best_image_bytes = buffer.getvalue()
            encoding_time = end_time - start_time
            
        if(size > target_bytes):
            max_q = q - 1
        else:
            min_q = q + 1
            
        if(min_q > max_q):
            break

    # Save the absolute best match to the actual hard drive
    with open(output_path, "wb") as f:
        f.write(best_image_bytes)

    actual_bpp = (len(best_image_bytes) * 8) / (width * height)
    
    print(f"  -> SUCCESS! Saved: {output_path}")
    print(f"  -> Best Quality Setting: {best_q}")
    print(f"  -> Actual Size: {len(best_image_bytes)} bytes ({actual_bpp:.3f} bpp)\n")
    
    return encoding_time


def process_single_image(input_file):
    print(f'Processing {input_file}')
    baseName = input_file.split('.')[0]
    baseDir = f'documents\\{input_file}'
    
    encoding_results = []
    
    try:
        for quality_level, target_bpp in tiers.items():
            print(f"--- Processing Quality Level {quality_level} ({target_bpp} bpp) ---")
            
            # 1. HEIC (HEIF format in pillow_heif)
            t = encode_to_target_bpp(baseDir, f"{OUT_PATH}\\{baseName}_{quality_level}.heic", "HEIF", target_bpp, chroma=420)
            encoding_results.append({"Original_Image": baseName, "Format": "HEIC", "Quality_Level": quality_level, "Encoding_Time_sec": t})
            
            # 2. AVIF
            t = encode_to_target_bpp(baseDir, f"{OUT_PATH}\\{baseName}_{quality_level}.avif", "AVIF", target_bpp, chroma=420)
            encoding_results.append({"Original_Image": baseName, "Format": "AVIF", "Quality_Level": quality_level, "Encoding_Time_sec": t})
            
            # 3. WebP
            t = encode_to_target_bpp(baseDir, f"{OUT_PATH}\\{baseName}_{quality_level}.webp", "WEBP", target_bpp, method=6) # method=6 is max compression effort
            encoding_results.append({"Original_Image": baseName, "Format": "WEBP", "Quality_Level": quality_level, "Encoding_Time_sec": t})
            
            # 4. JPEG
            t = encode_to_target_bpp(baseDir, f"{OUT_PATH}\\{baseName}_{quality_level}.jpg", "JPEG", target_bpp, subsampling=1) # subsampling=1 is 4:2:0
            encoding_results.append({"Original_Image": baseName, "Format": "JPEG", "Quality_Level": quality_level, "Encoding_Time_sec": t})
            
    except Exception as e:
        print(f"Error processing '{input_file}': {e}")
    
    print(f'Finished processing {input_file}')
    return encoding_results

# ==========================================
# Example Pipeline Execution
# ==========================================

# Define our target tiers
tiers = {
    3: 1.5, ## high quality 16:1 ratio
    2: 0.57, ## medium 42:1
    1: 0.25 ## low quality 96:1
}

OUT_PATH = 'encoding_results\\compressed_images'

if(__name__ == "__main__"):
    
    files_to_process = []
    '''
    for i in os.listdir('originals'):
        if(i.split('.')[1] == 'tif'):
            files_to_process.append(i)
    '''
            
    for i in os.listdir('documents'):
        files_to_process.append(i)
    
    all_encoding_results = []
    
    print(f"Starting parallel batch processing for {len(files_to_process)} images...")

    # max_workers dictates how many files process at the exact same time.
    with ProcessPoolExecutor(max_workers = 4) as executor:
        futures = {}
        for file in files_to_process:
            # 1. Schedule the function to run
            future_object = executor.submit(process_single_image, file)
            # 2. Add it to the dictionary where Key = future_object, Value = file
            futures[future_object] = file
        
        # As each image fully finishes, gather its results
        for future in as_completed(futures):
            image_results = future.result()
            all_encoding_results.extend(image_results) # Flattens the list of lists

    # Save the consolidated CSV
    df_times = pd.DataFrame(all_encoding_results)
    df_times.to_csv("encoding_results\\encoding_times.csv", index=False, mode='a',
        header=not os.path.exists("encoding_results\\encoding_times.csv"))
    print("\nAll encoding complete! Saved combined encoding_times.csv.")
    
