from PIL import Image

def convert_to_ppm(input_path, output_path):
    img = Image.open(input_path)
    
    # Convert to RGB and 8-bit
    img = img.convert("RGB")
    
    img.save(output_path, format="PPM")


# Example usage
## convert_to_ppm("DSC02435.tif", "reference.ppm")
convert_to_ppm("DSC02435_02.jpg", "compressed.ppm")
