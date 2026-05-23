import os
import cv2
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np

def save_diff_maps(reference_path, compressed_path, out_path, amp_factor = 10):
    """
    Calculates, plots, and saves the amplified and normalized differences 
    between the image arrays.
    """
    plt.style.use('dark_background')

    # Open images and convert to YCbCr space to explicitly isolate the Y channel
    ref_img = Image.open(reference_path).convert('YCbCr')
    comp_img = Image.open(compressed_path).convert('YCbCr')
    
    # Extract Y channel (index 0) and cast to int16 to avoid uint8 underflow on subtraction
    ref_y = np.array(ref_img.getchannel(0), dtype=np.int16)
    comp_y = np.array(comp_img.getchannel(0), dtype=np.int16)
    
    # Calculate absolute pixel difference on the Y channel
    diff = np.abs(ref_y - comp_y)
    
    base_filename = os.path.splitext(os.path.basename(compressed_path))[0]
    
    # ---------------------------------------------------------
    # 1. Amplified Difference Map
    # ---------------------------------------------------------
    # Multiply by amp_factor and cap at 255
    diff_amplified = np.clip(diff * amp_factor, 0, 255).astype(np.uint8)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(diff_amplified, cmap='gray')
    plt.title(f"Amplified Difference Image (Y Channel, Amp={amp_factor})")
    plt.savefig(os.path.join(out_path, "Diff_Map_Amp.png"), bbox_inches='tight', pad_inches=0.1, dpi = 200)
    plt.close()
    
    # ---------------------------------------------------------
    # 2. Normalized Difference Map
    # ---------------------------------------------------------
    diff_min = diff.min()
    diff_max = diff.max()
    
    # Prevent division by zero if images are mathematically identical
    if diff_max == diff_min:
        diff_norm = np.zeros_like(diff, dtype=np.uint8)
    else:
        # Scale differences to span the full 0-255 range
        diff_norm = ((diff - diff_min) / (diff_max - diff_min) * 255.0).astype(np.uint8)
        
    plt.figure(figsize=(10, 8))
    plt.imshow(diff_norm, cmap='gray')
    plt.title("Normalized Difference Image (Y Channel)")
    plt.savefig(os.path.join(out_path, "Diff_Map_Norm.png"), bbox_inches='tight', pad_inches=0.1, dpi = 200)
    plt.close()