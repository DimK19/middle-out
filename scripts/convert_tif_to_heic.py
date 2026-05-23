import warnings
from PIL import Image
from pillow_heif import register_heif_opener

## Silence the annoying and pointless metadata warning from the TIFF plugin
## "Metadata Warning, tag 33723 had too many entries: 2, expected 1"
warnings.filterwarnings("ignore", category=UserWarning, module="PIL.TiffImagePlugin")

# This single line tells Pillow how to read/write HEIF files
register_heif_opener()

input_tiff = "DSC02435.tif"
output_heic = "DSC02435_03.heic"

# 1. Open the 8-bit tif file directly in Python so it stays open
with open(input_tiff, "rb") as f:
    img = Image.open(f)
    
    # 2. Save it as 8-bit heic while the file pointer 'f' is still strictly open
    img.save(
        output_heic,
        format="HEIF",
        quality=10,     # Adjust quality from 1-100
        chroma=420      # 4:2:0 chroma subsampling (standard for JPEGs/Web)
    )

print(f"Successfully converted {input_tiff} to {output_heic}")
