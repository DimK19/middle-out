import numpy as np
from PIL import Image
import os
import math
from skimage.metrics import structural_similarity as ssim
from pillow_heif import register_heif_opener

register_heif_opener()

# -----------------------------
# Image loading
# -----------------------------
def load_image(path, grayscale=True):
    img = Image.open(path)
    
    if grayscale:
        img = img.convert("L")  # convert to grayscale
    
    return np.array(img, dtype=np.float32)


# -----------------------------
# Mean Squared Error
# -----------------------------
def mean_squared_error(original, compressed):
    diff = original - compressed
    mse = np.mean(diff ** 2)
    return mse


# -----------------------------
# Peak Signal-to-Noise Ratio
# -----------------------------
def peak_signal_to_noise_ratio(original, compressed):
    mse = mean_squared_error(original, compressed)
    
    if mse == 0:
        return float('inf')  # perfect match
    
    max_pixel = 255.0
    psnr = 10 * math.log10((max_pixel ** 2) / mse)
    return psnr

# -----------------------------
# Structural Similarity Index Measure
# -----------------------------    
def structural_similarity_index(original, compressed):
    ssim_value = ssim(original, compressed, data_range=255)
    return ssim_value


# -----------------------------
# Bits per pixel
# -----------------------------
def bits_per_pixel(file_path, width, height):
    size_bytes = os.path.getsize(file_path)
    size_bits = size_bytes * 8
    return size_bits / (width * height)


# -----------------------------
# Combined evaluation
# -----------------------------
def evaluate(original_path, compressed_path):
    original = load_image(original_path)
    compressed = load_image(compressed_path)

    if original.shape != compressed.shape:
        raise ValueError("Images must have the same dimensions")

    height, width = original.shape

    mse = mean_squared_error(original, compressed)
    psnr = peak_signal_to_noise_ratio(original, compressed)
    bpp = bits_per_pixel(compressed_path, width, height)
    ssim_val = structural_similarity_index(original, compressed)

    return {
        "mean_squared_error": mse,
        "peak_signal_to_noise_ratio": psnr,
        "bits_per_pixel": bpp,
        "ssim": ssim_val
    }
