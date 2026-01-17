import cv2
import numpy as np
import pyautogui
from hand_tracking import HandTracker
from face_tracking import FaceTracker
from gesture_recognition import GestureRecognizer
from hud_renderer import HUDRenderer

# Configure PyAutoGUI
# Set failsafe to True but we clamp coordinates to avoid the corners
pyautogui.FAILSAFE = True
SCREEN_W, SCREEN_H = pyautogui.size()

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize modules
    hand_tracker = HandTracker(max_num_hands=1, min_detection_confidence=0.8)
    face_tracker = FaceTracker(max_num_faces=1)
    recognizer = GestureRecognizer()
    renderer = HUDRenderer()
    
    clicking = False
    right_clicking = False
    kb_mode = False
    mouse_active = True
    active_key = None
    
    print("="*40)
    print(" HCI SYSTEM V3.4 - TERMINAL ACCESS READY ")
    print("="*40)
    print("SAFETY CONTROLS:")
    print(" - Press 'M' to Toggle AI Mouse Control")
    print(" - Press 'K' to Toggle Virtual Keyboard")
    print(" - Press 'Q' to Terminate System")
    print("\nOPERATION MANUAL:")
    print(" 1. Move Mouse: Point index (when active)")
    print(" 2. Pause AI: Press 'M' to use physical mouse")
    print(" 3. Switch Window: Vertical Swipe (Alt+Tab)")
    print("="*40)

    while True:
        success, img = cap.read()
        if not success:
            break
            
        h_cam, w_cam, _ = img.shape
        img = cv2.flip(img, 1)
        
        # 1. Track Hands & Analytics
        img = hand_tracker.find_hands(img, draw=False)
        hand_lms = hand_tracker.get_landmarks(img)
        
        # 2. Track Face Mesh
        img, face_lms = face_tracker.find_face_mesh(img, draw=False)
        
        # 3. Recognize Gestures
        gesture = "None"
        swipe = None
        analytics = None
        active_key = None
        
        if hand_lms:
            gesture = recognizer.get_gesture(hand_lms)
            swipe = recognizer.detect_swipe(hand_lms)
            analytics = recognizer.analytics
            
            # --- CURSOR & CLICKS ---
            target_x = np.interp(analytics['screen_pos'][0], (150, w_cam-150), (2, SCREEN_W - 2))
            target_y = np.interp(analytics['screen_pos'][1], (150, h_cam-150), (2, SCREEN_H - 2))
            
            # Only move mouse if AI control is active
            if mouse_active:
                try:
                    pyautogui.moveTo(target_x, target_y, _pause=False)
                except: pass
            
            # --- KEYBOARD COLLISION ---
            if kb_mode:
                cur_x, cur_y = analytics['screen_pos']
                keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
                start_x, start_y = 400, 450
                k_size, gap = 50, 10
                for r_idx, row in enumerate(keys):
                    for c_idx, char in enumerate(row):
                        kx = start_x + (c_idx * (k_size + gap)) + (r_idx * 20)
                        ky = start_y + (r_idx * (k_size + gap))
                        if kx < cur_x < kx + k_size and ky < cur_y < ky + k_size:
                            active_key = char
            
            # --- GESTURE EXECUTION ---
            if gesture == "Pinch":
                if not clicking:
                    if kb_mode and active_key:
                        pyautogui.press(active_key.lower())
                    elif mouse_active:
                        pyautogui.click()
                    clicking = True
            else:
                clicking = False
                
            if gesture == "Two-Finger" and mouse_active:
                if not right_clicking:
                    pyautogui.rightClick()
                    right_clicking = True
            else:
                right_clicking = False

            # --- SCREEN / WINDOW SWITCHING ---
            if swipe == "Left":
                pyautogui.hotkey('ctrl', 'win', 'left')
            elif swipe == "Right":
                pyautogui.hotkey('ctrl', 'win', 'right')
            elif swipe == "Up" or swipe == "Down":
                pyautogui.hotkey('alt', 'tab')
            
        # 4. Render AR HUD
        img = renderer.draw_hud(img, hand_lms, face_lms, gesture, swipe, analytics, kb_mode, active_key)
        
        # Display
        cv2.imshow("HCI Workstation Interface", img)
        
        # Hotkeys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('k'):
            kb_mode = not kb_mode
        elif key == ord('m'):
            mouse_active = not mouse_active
            print(f"[SYSTEM] AI Mouse Control: {'ENABLED' if mouse_active else 'DISABLED (Terminal Safety)'}")
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
