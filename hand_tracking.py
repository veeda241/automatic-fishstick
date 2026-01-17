import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.landmark_history = []
        self.smoothing_window = 5

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def get_landmarks(self, img, hand_idx=0):
        landmarks = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_idx:
                my_hand = self.results.multi_hand_landmarks[hand_idx]
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.append([id, cx, cy, lm.z])
                
                # Apply basic smoothing
                landmarks = self._smooth_landmarks(landmarks)
                
        return landmarks

    def _smooth_landmarks(self, landmarks):
        if not landmarks:
            return []
            
        self.landmark_history.append(landmarks)
        if len(self.landmark_history) > self.smoothing_window:
            self.landmark_history.pop(0)
            
        avg_landmarks = []
        for i in range(len(landmarks)):
            sum_x = sum(h[i][1] for h in self.landmark_history)
            sum_y = sum(h[i][2] for h in self.landmark_history)
            avg_x = int(sum_x / len(self.landmark_history))
            avg_y = int(sum_y / len(self.landmark_history))
            avg_landmarks.append([landmarks[i][0], avg_x, avg_y, landmarks[i][3]])
            
        return avg_landmarks

    def get_hand_type(self, hand_idx=0):
        if self.results.multi_handedness:
            if len(self.results.multi_handedness) > hand_idx:
                return self.results.multi_handedness[hand_idx].classification[0].label
        return None
