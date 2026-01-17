import cv2
import time
from .config import *

# ======================== MENU MODE ========================
menu_hover_start = 0
menu_hover_option = -1

def draw_menu(img, finger_pos, finger_count, landmarks, current_mode):
    global menu_hover_start, menu_hover_option
    
    # Title
    cv2.putText(img, "HAND GESTURE CONTROLLER", (wCam//2 - 280, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, NEON_CYAN, 3)
    
    # Draw hand detection indicator - Move to bottom center
    if finger_pos:
        cv2.putText(img, "HAND DETECTED", (wCam//2 - 100, hCam - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_GREEN, 2)
    else:
        cv2.putText(img, "NO HAND - Show your hand!", (wCam//2 - 180, hCam - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, NEON_RED, 2)
    
    # Menu buttons - BIGGER and easier to hit
    buttons = [
        ("1. GESTURE CONTROL", NEON_PINK, 180),
        ("2. DRAWING MODE", NEON_GREEN, 290),
        ("3. SNAKE GAME", NEON_ORANGE, 400),
        ("4. INVISIBLE CLOAK", NEON_RED, 510),
    ]
    
    selected = -1
    btn_w, btn_h = 500, 80  # Bigger buttons
    btn_x = wCam//2 - btn_w//2
    
    new_mode = current_mode

    # Draw buttons and check hover
    for i, (text, color, y) in enumerate(buttons):
        is_hovering = False
        if finger_pos:
            if btn_x < finger_pos[0] < btn_x + btn_w and y < finger_pos[1] < y + btn_h:
                is_hovering = True
                selected = i + 1
        
        # Draw button
        if is_hovering:
            cv2.rectangle(img, (btn_x, y), (btn_x + btn_w, y + btn_h), color, -1)
            cv2.rectangle(img, (btn_x, y), (btn_x + btn_w, y + btn_h), WHITE, 3)
            text_color = WHITE
        else:
            cv2.rectangle(img, (btn_x, y), (btn_x + btn_w, y + btn_h), color, 2)
            text_color = color
        
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        text_x = btn_x + (btn_w - text_size[0]) // 2
        text_y = y + (btn_h + text_size[1]) // 2
        cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, text_color, 2)
        
        # Progress bar for hold-to-select
        if is_hovering and menu_hover_option == selected:
            elapsed = time.time() - menu_hover_start
            progress = min(1.0, elapsed / 1.5)
            bar_width = int(btn_w * progress)
            cv2.rectangle(img, (btn_x, y + btn_h + 5), (btn_x + bar_width, y + btn_h + 15), NEON_GREEN, -1)
            cv2.rectangle(img, (btn_x, y + btn_h + 5), (btn_x + btn_w, y + btn_h + 15), WHITE, 1)
            
            # Check if held long enough
            if progress >= 1.0:
                new_mode = selected
                menu_hover_option = -1
                print(f"[MENU] Selected mode {selected} via HOLD")
                return new_mode
    
    # Handle hover timing
    if selected > 0:
        if menu_hover_option != selected:
            menu_hover_option = selected
            menu_hover_start = time.time()
    else:
        menu_hover_option = -1
        menu_hover_start = time.time()
    
    # FIST (0 fingers) to confirm while hovering
    if selected > 0 and finger_count == 0:
        new_mode = selected
        print(f"[MENU] Selected mode {selected} via FIST")
        time.sleep(0.3)
        return new_mode
    
    # Show finger pointer
    if finger_pos:
        cv2.circle(img, finger_pos, 20, NEON_PINK, -1)
        cv2.circle(img, finger_pos, 30, NEON_PINK, 3)
        # Show coordinates for debugging
        cv2.putText(img, f"Pos: {finger_pos}", (finger_pos[0] + 30, finger_pos[1]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_YELLOW, 1)
    
    # Instructions
    cv2.putText(img, "HOLD on button for 1.5s OR make FIST to select", 
                (wCam//2 - 250, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.putText(img, "Keyboard: Press 1, 2, or 3 to select | Q to quit", 
                (wCam//2 - 230, hCam - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, NEON_YELLOW, 1)
    
    # Debug info
    cv2.putText(img, f"Fingers: {finger_count} | Selected: {selected} | Hover: {menu_hover_option}", 
                (20, hCam - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    
    return new_mode
