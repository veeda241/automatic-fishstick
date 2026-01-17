import cv2
from hand_tracking import HandTracker
from gesture_recognition import GestureRecognizer
from hud_renderer import HUDRenderer

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize modules
    tracker = HandTracker(max_num_hands=1, min_detection_confidence=0.8)
    recognizer = GestureRecognizer()
    renderer = HUDRenderer()
    
    print("Iron Man AR System Initializing...")
    print("Press 'q' to exit.")

    while True:
        success, img = cap.read()
        if not success:
            break
            
        # Flip image for a mirror effect (more intuitive for AR)
        img = cv2.flip(img, 1)
        
        # 1. Track Hands
        img = tracker.find_hands(img, draw=False) # We'll do custom drawing
        landmarks = tracker.get_landmarks(img)
        
        # 2. Recognize Gestures
        gesture = "None"
        swipe = None
        if landmarks:
            gesture = recognizer.get_gesture(landmarks)
            swipe = recognizer.detect_swipe(landmarks)
            
        # 3. Render AR HUD
        img = renderer.draw_hud(img, landmarks, gesture, swipe)
        
        # Display
        cv2.imshow("Iron Man AR HUD", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
