import numpy as np
from PIL import Image
import os
import math
from skimage.metrics import structural_similarity as ssim
from pillow_heif import register_heif_opener

register_heif_opener()

# -----------------------------
# Load image as YCbCr
# -----------------------------
def load_image_ycbcr(path):
    img = Image.open(path).convert("YCbCr")
    return np.array(img, dtype=np.float32)


# -----------------------------
# MSE
# -----------------------------
def mse_channel(a, b):
    return np.mean((a - b) ** 2)


# -----------------------------
# PSNR
# -----------------------------
def psnr_channel(a, b):
    mse = mse_channel(a, b)
    if mse == 0:
        return float('inf')
    return 10 * math.log10((255.0 ** 2) / mse)


# -----------------------------
# SSIM + map
# -----------------------------
def ssim_channel(a, b, window_size = 11):
    value, ssim_map = ssim(a, b, win_size = window_size, data_range=255, full=True)
    return value, ssim_map


# -----------------------------
# Bits per pixel
# -----------------------------
def bits_per_pixel(file_path, width, height):
    size_bytes = os.path.getsize(file_path)
    return (size_bytes * 8) / (width * height)


# -----------------------------
# Full evaluation
# -----------------------------
def evaluate_ycbcr(original_path, compressed_path, window_sizes = (7, 11, 13)):
    original = load_image_ycbcr(original_path)
    compressed = load_image_ycbcr(compressed_path)

    if original.shape != compressed.shape:
        raise ValueError("Images must match")

    height, width, _ = original.shape

    channels = ["Y", "Cb", "Cr"]
    results = {}
    ssim_maps = {}

    for i, ch in enumerate(channels):
        orig_c = original[:, :, i]
        comp_c = compressed[:, :, i]

        mse = mse_channel(orig_c, comp_c)
        psnr = psnr_channel(orig_c, comp_c)
        ssim_val, ssim_map = ssim_channel(orig_c, comp_c)

        results[ch] = {
            "mse": mse,
            "psnr": psnr,
            "ssim": {}
        }
        ssim_maps[ch] = {}

        # Loop through the requested window sizes
        for w in window_sizes:
            ssim_val, ssim_map = ssim_channel(orig_c, comp_c, window_size=w)
            results[ch]["ssim"][w] = ssim_val
            ssim_maps[ch][w] = ssim_map

    bpp = bits_per_pixel(compressed_path, width, height)

    return {
        "per_channel": results,
        "bits_per_pixel": bpp,
        "ssim_maps": ssim_maps
    }