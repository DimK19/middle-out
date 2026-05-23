from PIL import Image

# 1. Open your uncompressed or high-quality source image
# (Use a PNG, TIFF, or BMP so you aren't compounding JPEG artifacts)
img = Image.open("documents/DOC01.png")

# 2. Define your Custom Luminance Table (Brightness/Structure)
# This is a flat list of 64 integers representing the 8x8 matrix.
# Lower numbers = higher quality / less compression.
# Higher numbers (up to 255) = lower quality / more compression.
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

# 3. Define your Custom Chrominance Table (Color)
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

# 4. Save the image, passing the tables directly to the encoder
# Note: Pillow expects a list containing the Luma and Chroma tables.
img.save(
    "DOC01_custom_dct.jpg", 
    "JPEG", 
    qtables=[luma_q10, chroma_q10],
    optimize = True
)

print("Custom JPEG saved successfully!")
