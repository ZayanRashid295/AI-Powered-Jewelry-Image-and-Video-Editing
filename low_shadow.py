import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
import os
import io

def apply_subtle_shadow(img_array, shadow_height=15, opacity=0.08):
    """Apply a very subtle, dull shadow at the bottom"""
    h, w = img_array.shape[:2]
    
    # Create a barely noticeable gray shadow
    shadow = np.zeros((h, w, 3), dtype=np.float32)
    shadow_color = np.array([240, 240, 240])  # Very light gray (almost white)
    
    # Create smooth gradient
    for i in range(shadow_height):
        weight = (opacity * (shadow_height - i) / shadow_height)
        shadow[h - i - 1, :] = shadow_color * weight
    
    # Blend with original image
    result = cv2.addWeighted(img_array.astype(np.float32), 1.0, 
                           shadow, 1.0, 0)
    
    return np.clip(result, 0, 255).astype(np.uint8)

def process_jewelry_image(input_path, output_folder):
    """Complete processing pipeline with subtle shadow"""
    os.makedirs(output_folder, exist_ok=True)
    
    # 1. Remove background
    with open(input_path, "rb") as f:
        img_no_bg = remove(f.read())
    
    # 2. Create pure white background
    img = Image.open(io.BytesIO(img_no_bg))
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    
    # 3. Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(white_bg), cv2.COLOR_RGB2BGR)
    
    # 4. Gentle enhancement (preserve highlights)
    lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Soft light enhancement
    l = np.clip(l * 1.1, 0, 255).astype(np.uint8)
    
    enhanced_lab = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # 5. Apply subtle shadow
    final = apply_subtle_shadow(enhanced)
    
    # 6. Save final image
    final_path = os.path.join(output_folder, "final_subtle_shadow.png")
    cv2.imwrite(final_path, cv2.cvtColor(final, cv2.COLOR_BGR2RGB))
    
    print(f"Professional result with subtle shadow saved to {final_path}")

# Example usage
input_image_path = r"C:\Users\Lenovo\Downloads\test_02.tif"
output_folder = r"C:\Users\Lenovo\OneDrive\Desktop\output"

process_jewelry_image(input_image_path, output_folder)