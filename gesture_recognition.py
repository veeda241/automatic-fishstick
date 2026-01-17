import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.pinch_threshold = 30
        self.fist_threshold = 50
        self.prev_center_x = None
        self.prev_center_y = None
        self.swipe_threshold = 15 # Lowered for per-frame detection
        self.swipe_cooldown = 0
        self.analytics = {
            "pinch_dist": 0,
            "index_middle_dist": 0,
            "hand_scale": 1.0,
            "screen_pos": (0, 0)
        }
        self.smoothened_x, self.smoothened_y = 0, 0
        self.smooth_factor = 7
        self.base_click_threshold = 30 
        
    def get_gesture(self, landmarks):
        if not landmarks:
            return "None"
            
        # Landmark IDs:
        # 4: Thumb Tip
        # 8: Index Tip
        # 12: Middle Tip
        # 16: Ring Tip
        # 20: Pinky Tip
        # 0: Wrist
        
        # Calculate distance between thumb and index tips for pinch
        thumb_tip = np.array([landmarks[4][1], landmarks[4][2]])
        index_tip = np.array([landmarks[8][1], landmarks[8][2]])
        pinch_dist = np.linalg.norm(thumb_tip - index_tip)
        self.analytics["pinch_dist"] = int(pinch_dist)

        # Distance between index and middle (for potential slider control)
        middle_tip = np.array([landmarks[12][1], landmarks[12][2]])
        im_dist = np.linalg.norm(index_tip - middle_tip)
        self.analytics["index_middle_dist"] = int(im_dist)

        # Scale estimate based on palm size (Distance between wrist and index MCP)
        wrist = np.array([landmarks[0][1], landmarks[0][2]])
        index_mcp = np.array([landmarks[5][1], landmarks[5][2]])
        self.analytics["hand_scale"] = np.linalg.norm(wrist - index_mcp)
        
        # Screen Position Mapping (using index finger Tip 8)
        ix, iy = landmarks[8][1], landmarks[8][2]
        # Smooth movement
        self.smoothened_x = self.smoothened_x + (ix - self.smoothened_x) / self.smooth_factor
        self.smoothened_y = self.smoothened_y + (iy - self.smoothened_y) / self.smooth_factor
        self.analytics["screen_pos"] = (int(self.smoothened_x), int(self.smoothened_y))
        
        # Check if fingers are extended (Open Palm vs Fist)
        fingers = []
        # Thumb: check if thumb tip is to the right/left of thumb IP joint depending on hand
        # For simplicity, we can use distance from wrist or relative position
        # A more robust way is checking the angle or Y coordinate for non-thumb fingers
        
        # Index, Middle, Ring, Pinky
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        extended_count = 0
        for tip, pip in zip(tips, pips):
            if landmarks[tip][2] < landmarks[pip][2]: # Tip is above PIP joint
                extended_count += 1
                
        # Dynamic click threshold based on hand scale (distance from wrist to index MCP)
        # Larger hand scale = closer to camera = larger threshold
        dynamic_threshold = self.base_click_threshold * (self.analytics["hand_scale"] / 80.0)
        dynamic_threshold = max(20, min(50, dynamic_threshold))

        # Gesture Logic
        if extended_count == 0:
            return "Fist"
        elif pinch_dist < dynamic_threshold:
            return "Pinch"
        elif extended_count >= 4:
            return "Open Palm"
            
        return "Unknown"

    def detect_swipe(self, landmarks):
        if not landmarks:
            return None
            
        center_x = landmarks[9][1] # Middle finger MCP joint as center
        center_y = landmarks[9][2]
        swipe = None
        
        if self.prev_center_x is not None and self.prev_center_y is not None:
            diff_x = center_x - self.prev_center_x
            diff_y = center_y - self.prev_center_y
            
            if self.swipe_cooldown == 0:
                # Detect horizontal swipe
                if abs(diff_x) > self.swipe_threshold and abs(diff_x) > abs(diff_y):
                    if diff_x > 0: swipe = "Right"
                    else: swipe = "Left"
                    self.swipe_cooldown = 15
                # Detect vertical swipe
                elif abs(diff_y) > self.swipe_threshold and abs(diff_y) > abs(diff_x):
                    if diff_y > 0: swipe = "Down"
                    else: swipe = "Up"
                    self.swipe_cooldown = 15
                
        self.prev_center_x = center_x
        self.prev_center_y = center_y
        if self.swipe_cooldown > 0:
            self.swipe_cooldown -= 1
            
        return swipe
