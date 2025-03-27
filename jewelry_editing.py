import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
import os
import io

def whiten_diamonds(img_array):
    """Special treatment to enhance diamonds/white gems"""
    # Convert to HSV color space
    hsv = cv2.cvtColor(img_array, cv2.COLOR_BGR2HSV)
    
    # Define white color range in HSV (adjust these values as needed)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([180, 30, 255], dtype=np.uint8)
    
    # Create mask for white areas
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Create white overlay
    white_overlay = np.full_like(img_array, 255)
    
    # Blend only where mask indicates white areas
    result = img_array.copy()
    result[white_mask > 0] = cv2.addWeighted(
        img_array[white_mask > 0], 
        0.7, 
        white_overlay[white_mask > 0], 
        0.3, 
        0
    )
    return result

def add_soft_shadow(img_array, shadow_height=20, blur_radius=15, opacity=0.15):
    """Adds a soft shadow at the bottom of the image"""
    h, w = img_array.shape[:2]
    shadow = np.zeros((h, w), dtype=np.float32)
    
    # Create gradient
    gradient = np.linspace(0, 1, shadow_height)
    shadow[-shadow_height:] = gradient[::-1].reshape(-1, 1)
    
    # Apply blur and opacity
    shadow = cv2.GaussianBlur(shadow, (blur_radius, blur_radius), 0)
    shadow = (shadow * opacity * 255).astype(np.uint8)
    
    # Apply to image
    result = img_array.copy()
    for c in range(3):  # Apply to all channels
        result[..., c] = np.where(shadow > 0,
                                np.minimum(result[..., c], 255 - shadow),
                                result[..., c])
    return result

def process_jewelry_image(input_path, output_folder):
    """Complete processing pipeline"""
    os.makedirs(output_folder, exist_ok=True)
    
    # 1. Remove background
    with open(input_path, "rb") as f:
        img_no_bg = remove(f.read())
    
    # 2. Create white background
    img = Image.open(io.BytesIO(img_no_bg))
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    
    # 3. Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(white_bg), cv2.COLOR_RGB2BGR)
    
    # 4. Special diamond whitening
    whitened = whiten_diamonds(cv_img)
    
    # 5. Gentle enhancement
    lab = cv2.cvtColor(whitened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Brighten without creating dark artifacts
    l = cv2.add(l, 20)  # Simple brightness boost
    l = np.clip(l, 0, 255)
    
    enhanced_lab = cv2.merge((l, a, b))
    corrected = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # 6. Add soft shadow
    final = add_soft_shadow(corrected)
    
    # 7. Save final image
    final_path = os.path.join(output_folder, "final_result.png")
    cv2.imwrite(final_path, cv2.cvtColor(final, cv2.COLOR_BGR2RGB))
    
    print(f"Final result saved to {final_path}")

# Example usage
input_image_path = r"C:\Users\Lenovo\Downloads\test_02.tif"
output_folder = r"C:\Users\Lenovo\OneDrive\Desktop\output"

process_jewelry_image(input_image_path, output_folder)