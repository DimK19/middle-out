import time
import pandas as pd
from pathlib import Path
from PIL import Image
import os

# Assume image_files is your list of file paths
results = []

luma_q10 = [
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255
]

chroma_q10 = [
   250, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255,
   255, 255, 255, 255, 255, 255, 255, 255
]

for i in os.listdir('documents'):
    
    # 1. Open your uncompressed or high-quality source image
    # (Use a PNG, TIFF, or BMP so you aren't compounding JPEG artifacts)
    img = Image.open(f"documents/{i}")

    img_name = i.split('.')[0]
    start_time = time.perf_counter()
    img.save(
        os.path.join('encoding_results', 'compressed_images', f'{img_name}_1.jpg'), 
        "JPEG", 
        qtables=[luma_q10, chroma_q10],
        optimize = True
    )
    end_time = time.perf_counter()
    encoding_time = end_time - start_time
    
    results.append({
        'Original_Image': img_name,
        'Format': 'JPEG',
        'Quality_Level': '1',
        'Encoding_Time_sec': encoding_time
    })

# Append results to the existing CSV
if results:
    df = pd.DataFrame(results)
    csvdir = os.path.join("encoding_results", "encoding_times.csv")
    df.to_csv(csvdir, mode='a', header=False, index=False)