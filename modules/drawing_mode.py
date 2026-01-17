import cv2
import numpy as np
from .config import *

# ======================== DRAWING MODE ========================
# Drawing state
canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)
draw_color_index = 0
brush_size = 10
prev_draw_point = None

def drawing_mode(img, landmarks, fingers, finger_count):
    global canvas, draw_color_index, brush_size, prev_draw_point
    
    index_tip = landmarks[8]
    
    # Draw color palette at top
    palette_y = 30
    for i, (color, name) in enumerate(zip(DRAW_COLORS, COLOR_NAMES)):
        x = 50 + i * 80
        cv2.rectangle(img, (x, palette_y), (x + 60, palette_y + 50), color, -1 if i == draw_color_index else 2)
        if i == draw_color_index:
            cv2.rectangle(img, (x-3, palette_y-3), (x + 63, palette_y + 53), WHITE, 2)
    
    # Clear button
    cv2.rectangle(img, (wCam - 150, palette_y), (wCam - 50, palette_y + 50), NEON_RED, 2)
    cv2.putText(img, "CLEAR", (wCam - 140, palette_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_RED, 2)
    
    # Brush size indicator
    cv2.circle(img, (wCam - 200, palette_y + 25), brush_size, DRAW_COLORS[draw_color_index], -1)
    cv2.putText(img, f"Size: {brush_size}", (wCam - 230, palette_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    
    # Instructions
    cv2.putText(img, "1 Finger: Draw | 2 Fingers: Select Color | 5 Fingers: Clear | 3 Fingers: Size", 
                (20, hCam - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    
    # 1 FINGER: Draw
    if finger_count == 1 and fingers[1] == 1:
        cv2.circle(img, index_tip, brush_size, DRAW_COLORS[draw_color_index], -1)
        
        if prev_draw_point is not None:
            cv2.line(canvas, prev_draw_point, index_tip, DRAW_COLORS[draw_color_index], brush_size * 2)
        prev_draw_point = index_tip
    else:
        prev_draw_point = None
    
    # 2 FINGERS: Select Color (hover over palette)
    if finger_count == 2:
        if palette_y < index_tip[1] < palette_y + 50:
            for i in range(len(DRAW_COLORS)):
                x = 50 + i * 80
                if x < index_tip[0] < x + 60:
                    draw_color_index = i
                    break
        # Check clear button
        if wCam - 150 < index_tip[0] < wCam - 50 and palette_y < index_tip[1] < palette_y + 50:
            canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)
    
    # 3 FINGERS: Change brush size
    if finger_count == 3:
        palm_y = sum([landmarks[i][1] for i in [0, 5, 9, 13, 17]]) // 5
        brush_size = max(5, min(50, int(np.interp(palm_y, (150, hCam - 150), (50, 5)))))
    
    # 5 FINGERS: Clear canvas
    if finger_count == 5:
        canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)
    
    # Blend canvas with camera
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
    canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    cv2.add(img_bg, canvas_fg, img)

def get_canvas():
    global canvas
    return canvas

def show_canvas(img):
    global canvas
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
    canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    cv2.add(img_bg, canvas_fg, img)
