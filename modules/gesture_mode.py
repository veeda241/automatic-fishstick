import cv2
import pyautogui
import numpy as np
import time
from .config import *
from .utils import get_distance

# ======================== GESTURE CONTROL MODE ========================
pLocX, pLocY = 0, 0
cLocX, cLocY = 0, 0
last_click_time = 0  # For click debounce
last_switch_time = 0  # For app switch debounce

def gesture_control_mode(img, landmarks, fingers, finger_count, handedness):
    global pLocX, pLocY, cLocX, cLocY, last_click_time, last_switch_time
    
    mode = "DETECTING..."
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    
    palm_points = [0, 5, 9, 13, 17]
    palm_x = sum([landmarks[i][0] for i in palm_points]) // 5
    palm_y = sum([landmarks[i][1] for i in palm_points]) // 5
    
    # Draw HUD
    overlay = img.copy()
    cv2.rectangle(overlay, (10, 10), (350, 160), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    cv2.putText(img, "GESTURE CONTROL", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_PINK, 2)
    
    # Draw gesture guide
    cv2.putText(img, "1 Finger=Move | 2 Fingers=Click | 3=Scroll | 5=Switch", 
                (20, hCam - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_CYAN, 1)
    
    # 1 FINGER: Move Cursor
    if finger_count == 1 and fingers[1] == 1:
        mode = "MOVE CURSOR"
        x1, y1 = index_tip
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        cLocX = pLocX + (x3 - pLocX) / smoothening
        cLocY = pLocY + (y3 - pLocY) / smoothening
        pyautogui.moveTo(cLocX, cLocY)
        pLocX, pLocY = cLocX, cLocY
        cv2.circle(img, index_tip, 20, NEON_PINK, -1)
        cv2.circle(img, index_tip, 30, NEON_PINK, 2)

    # 2 FINGERS: Click (EASIER - just show 2 fingers and pinch)
    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
        length = get_distance(index_tip, middle_tip)
        mid_point = ((index_tip[0] + middle_tip[0]) // 2, (index_tip[1] + middle_tip[1]) // 2)
        
        # Draw visual feedback
        cv2.line(img, index_tip, middle_tip, NEON_GREEN, 4)
        cv2.circle(img, mid_point, 15, NEON_GREEN, 2)
        
        # Show distance (helps user understand)
        cv2.putText(img, f"Distance: {length}px", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_YELLOW, 1)
        
        # Progress bar for click
        progress = max(0, min(100, int((80 - length) * 1.5)))
        cv2.rectangle(img, (20, 140), (20 + progress * 2, 155), NEON_GREEN, -1)
        cv2.rectangle(img, (20, 140), (220, 155), WHITE, 1)
        
        current_time = time.time()
        
        # CLICK when fingers are close (threshold: 60px - much easier!)
        if length < 60 and (current_time - last_click_time) > 0.5:
            pyautogui.click()
            last_click_time = current_time
            mode = "CLICKED!"
            cv2.circle(img, mid_point, 60, NEON_GREEN, -1)
        elif length < 60:
            mode = "CLICK READY (wait)"
        else:
            mode = f"PINCH TO CLICK ({length}px)"

    # 3 FINGERS: Scroll
    elif finger_count == 3:
        mode = "SCROLL MODE"
        # Draw scroll zone indicator
        cv2.line(img, (wCam//2 - 100, hCam//2), (wCam//2 + 100, hCam//2), WHITE, 1)
        cv2.putText(img, "UP", (wCam//2 - 15, hCam//2 - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_CYAN, 2)
        cv2.putText(img, "DOWN", (wCam//2 - 30, hCam//2 + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_CYAN, 2)
        
        if palm_y < hCam // 2 - 50:
            pyautogui.scroll(3)
            mode = "SCROLLING UP"
            cv2.arrowedLine(img, (palm_x, palm_y + 50), (palm_x, palm_y - 50), NEON_GREEN, 5)
        elif palm_y > hCam // 2 + 50:
            pyautogui.scroll(-3)
            mode = "SCROLLING DOWN"
            cv2.arrowedLine(img, (palm_x, palm_y - 50), (palm_x, palm_y + 50), NEON_GREEN, 5)

    # 5 FINGERS: Switch Apps (with debounce)
    elif finger_count == 5:
        current_time = time.time()
        cv2.circle(img, (palm_x, palm_y), 80, NEON_ORANGE, 3)
        
        if (current_time - last_switch_time) > 1.5:
            pyautogui.hotkey('alt', 'tab')
            last_switch_time = current_time
            mode = "SWITCHED!"
            cv2.circle(img, (palm_x, palm_y), 100, NEON_ORANGE, -1)
        else:
            mode = "SWITCH (wait...)"
    
    cv2.putText(img, f"Mode: {mode}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.putText(img, f"Fingers: {finger_count}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
