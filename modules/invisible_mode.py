import cv2
import numpy as np
import time
from .config import *

# ======================== INVISIBLE CLOAK MODE ========================
background = None
capturing_background = True
capture_count = 0

# Default color (Blue-ish) - but will be calibrated
lower_bound = np.array([100, 50, 50])
upper_bound = np.array([130, 255, 255])

def init_invisible_cloak(cap, attempts=30):
    global background, capturing_background, capture_count
    
    print("Capturing background... Please move out of frame!")
    
    # Warm up and capture background
    for i in range(attempts):
        success, background = cap.read()
        if not success:
            continue
    
    background = cv2.flip(background, 1) # Flip to match mirror view
    capturing_background = False
    print("Background captured!")

def calibrate_color(img):
    global lower_bound, upper_bound
    
    # Sample center pixel
    h, w, _ = img.shape
    center_color = img[h//2, w//2]
    
    # Convert to HSV
    center_pixel = np.uint8([[center_color]])
    hsv_pixel = cv2.cvtColor(center_pixel, cv2.COLOR_BGR2HSV)[0][0]
    
    # Create range (Sensitivity +/- 10 for Hue, broad for Sat/Val)
    hue = hsv_pixel[0]
    lower_bound = np.array([max(0, hue - 10), 50, 50])
    upper_bound = np.array([min(179, hue + 10), 255, 255])
    
    print(f"Calibrated Hue: {hue}")
    return center_color

def invisible_cloak_mode(img):
    global background, lower_bound, upper_bound
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Create mask using calibrated bounds
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Refine mask (Clean up noise)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3), np.uint8))
    
    # Create the inverse mask (everything NOT cloak)
    mask_inv = cv2.bitwise_not(mask)
    
    # Segment 1: The cloak area (taken from background)
    res1 = cv2.bitwise_and(background, background, mask=mask)
    
    # Segment 2: The non-cloak area (taken from current frame)
    res2 = cv2.bitwise_and(img, img, mask=mask_inv)
    
    # Combine them
    final_output = cv2.addWeighted(res1, 1, res2, 1, 0)
    
    return final_output
