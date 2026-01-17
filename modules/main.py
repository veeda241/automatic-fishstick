import cv2
import numpy as np
import time
import os

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import mediapipe as mp
from modules.config import *
from modules.utils import count_fingers
import modules.menu_mode as menu_mode
import modules.gesture_mode as gesture_mode
import modules.drawing_mode as drawing_mode
import modules.snake_mode as snake_mode

# ======================== SETUP ========================
# MediaPipe Setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Camera Setup - Use DirectShow on Windows for better quality
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow for Windows

# Request Full HD resolution first (otherwise it often defaults to 640x480)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for less lag

# Read first frame to detect actual negotiated resolution
success, first_frame = cap.read()

if success:
    native_height, native_width = first_frame.shape[:2]
    from modules.config import set_resolution
    set_resolution(native_width, native_height)
    # Re-import wCam, hCam with updated values
    from modules.config import wCam, hCam
    print(f"  Camera native resolution: {native_width}x{native_height}")
    # Reinitialize modules that depend on resolution
    import importlib
    importlib.reload(drawing_mode)
    importlib.reload(snake_mode)
    importlib.reload(menu_mode)
    snake_mode.init_snake()
else:
    print("  Warning: Could not detect camera resolution, using default 1280x720")

# ======================== GLOBAL STATE ========================
current_mode = 0  # 0=Menu, 1=Gesture Control, 2=Drawing, 3=Snake Game

# ======================== MAIN LOOP ========================
print("\n" + "="*60)
print("   HAND GESTURE CONTROLLER - MULTI-MODE")
print("="*60)
print("\n  MODES:")
print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  1. GESTURE CONTROL - Control your computer")
print("  2. DRAWING MODE    - Draw with your finger")
print("  3. SNAKE GAME      - Play snake with gestures")
print("\n  Press 'M' to return to menu")
print("  Press 'Q' to quit")
print("="*60 + "\n")

prev_time = time.time()
frame_count = 0

cv2.namedWindow("Hand Gesture Controller", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Hand Gesture Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    
    if not success:
        break
    
    img = cv2.flip(img, 1)
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    frame_count += 1
    curr_time = time.time()
    fps = int(1 / (curr_time - prev_time + 0.001))
    prev_time = curr_time
    
    results = hands.process(imgRGB)
    
    finger_pos = None
    finger_count = 0
    fingers = [0, 0, 0, 0, 0]
    landmarks = None
    handedness = "Right"
    
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            
            handedness = handedness_info.classification[0].label
            landmarks = [(int(lm.x * wCam), int(lm.y * hCam)) for lm in hand_landmarks.landmark]
            finger_count, fingers = count_fingers(landmarks, handedness)
            finger_pos = landmarks[8]
    
    # Mode handling
    if current_mode == 0:  # Menu
        # draw_menu returns the new mode (or the same one)
        current_mode = menu_mode.draw_menu(img, finger_pos, finger_count, landmarks, current_mode)
        
    elif current_mode == 1:  # Gesture Control
        if landmarks:
            gesture_mode.gesture_control_mode(img, landmarks, fingers, finger_count, handedness)
        cv2.putText(img, "[M] Menu | [Q] Quit", (10, hCam - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
        
    elif current_mode == 2:  # Drawing
        if landmarks:
            drawing_mode.drawing_mode(img, landmarks, fingers, finger_count)
        else:
            drawing_mode.show_canvas(img)
        cv2.putText(img, "[M] Menu | [Q] Quit", (10, hCam - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
        
    elif current_mode == 3:  # Snake Game
        if landmarks:
            snake_mode.snake_game_mode(img, landmarks, fingers, finger_count, frame_count)
        else:
            cv2.putText(img, "Show your hand to play!", (wCam//2 - 180, hCam//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
        cv2.putText(img, "[M] Menu | [Q] Quit", (10, hCam - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    
    # FPS display
    cv2.putText(img, f"FPS: {fps}", (wCam - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_GREEN, 1)
    
    cv2.imshow("Hand Gesture Controller", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('m'):
        current_mode = 0
    # Keyboard shortcuts for menu
    elif key == ord('1') and current_mode == 0:
        current_mode = 1
        print("[KEYBOARD] Selected mode 1: GESTURE CONTROL")
    elif key == ord('2') and current_mode == 0:
        current_mode = 2
        print("[KEYBOARD] Selected mode 2: DRAWING")
    elif key == ord('3') and current_mode == 0:
        current_mode = 3
        print("[KEYBOARD] Selected mode 3: SNAKE GAME")

cap.release()
cv2.destroyAllWindows()
hands.close()
print("\nController stopped.")
