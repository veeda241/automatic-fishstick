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
    
    print("="*40)
    print(" HCI SYSTEM V3.1 - INDUSTRIAL INTERFACE ")
    print("="*40)
    print("Core Capabilities:")
    print(" - Precision Cursor Control (Mouse)")
    print(" - Gesture Input (Pinch-to-Click)")
    print(" - 3D Object Manipulation Engine")
    print("\nOPERATION MANUAL:")
    print(" 1. Align Index Tip for cursor tracking")
    print(" 2. Execute Pinch gesture for Input Trigger")
    print(" 3. Close hand (Fist) for Object Lock")
    print(" 4. Horizontal Swipe: Shift Virtual Desktop")
    print(" 5. Vertical Swipe: Switch Active Window (Alt+Tab)")
    print("\nPress 'Q' to terminate.")
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
        
        # 3. Recognize Gestures & Human-Computer Interaction
        gesture = "None"
        swipe = None
        analytics = None
        
        if hand_lms:
            gesture = recognizer.get_gesture(hand_lms)
            swipe = recognizer.detect_swipe(hand_lms)
            analytics = recognizer.analytics
            
            # --- PC CONTROL LOGIC ---
            # Map camera coordinates to Screen Resolution with buffer
            # Clamping the output to [2, size-2] to avoid the absolute corners (triggers failsafe)
            target_x = np.interp(analytics['screen_pos'][0], (150, w_cam-150), (2, SCREEN_W - 2))
            target_y = np.interp(analytics['screen_pos'][1], (150, h_cam-150), (2, SCREEN_H - 2))
            
            # Move Mouse
            try:
                # Use a small duration or pause to prevent overwhelming the OS
                pyautogui.moveTo(target_x, target_y, _pause=False)
            except: pass
            
            # Handling Clicks (Pinch)
            if gesture == "Pinch":
                if not clicking:
                    pyautogui.click()
                    clicking = True
            else:
                clicking = False

            # --- SCREEN / WINDOW SWITCHING ---
            if swipe == "Left":
                pyautogui.hotkey('ctrl', 'win', 'left')
            elif swipe == "Right":
                pyautogui.hotkey('ctrl', 'win', 'right')
            elif swipe == "Up" or swipe == "Down":
                # Quick Alt-Tab to switch to the most recent window
                pyautogui.hotkey('alt', 'tab')
            
        # 4. Render AR HUD
        img = renderer.draw_hud(img, hand_lms, face_lms, gesture, swipe, analytics)
        
        # Display
        cv2.imshow("HCI Workstation Interface", img)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
