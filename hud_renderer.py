import cv2
import numpy as np
import time

class HUDRenderer:
    def __init__(self):
        # Professional Industrial Workspace Colors
        self.primary_color = (180, 180, 180) # Modern Silver
        self.secondary_color = (255, 140, 0) # Safety Orange (HCI accent)
        self.accent_color = (0, 255, 0)     # Success Green
        self.bg_panel_color = (20, 20, 20)  # Deep Charcoal
        self.font = cv2.FONT_HERSHEY_DUPLEX
        
    def _project_3d(self, points, angle_x, angle_y, center, scale):
        projected = []
        rot_x = np.array([[1, 0, 0],
                         [0, np.cos(angle_x), -np.sin(angle_x)],
                         [0, np.sin(angle_x), np.cos(angle_x)]])
        
        rot_y = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                         [0, 1, 0],
                         [-np.sin(angle_y), 0, np.cos(angle_y)]])
        
        for p in points:
            rotated = np.dot(rot_x, p)
            rotated = np.dot(rot_y, rotated)
            z = 1 / (rotated[2] + 4)
            x = int(rotated[0] * z * scale + center[0])
            y = int(rotated[1] * z * scale + center[1])
            projected.append((x, y))
        return projected

    def draw_keyboard(self, img, active_key=None):
        # Keyboard Layout
        keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        start_x, start_y = 400, 450
        key_size = 50
        gap = 10
        
        overlay = img.copy()
        for r_idx, row in enumerate(keys):
            for c_idx, char in enumerate(row):
                x = start_x + (c_idx * (key_size + gap)) + (r_idx * 20)
                y = start_y + (r_idx * (key_size + gap))
                
                # Highlight if active
                color = self.secondary_color if char == active_key else (100, 100, 100)
                alpha = 0.8 if char == active_key else 0.4
                
                cv2.rectangle(overlay, (x, y), (x + key_size, y + key_size), (50, 50, 50), -1)
                cv2.rectangle(overlay, (x, y), (x + key_size, y + key_size), color, 2)
                cv2.putText(overlay, char, (x + 15, y + 35), self.font, 0.7, (255, 255, 255), 2)
        
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        return img

    def draw_hud(self, img, landmarks, face_landmarks, gesture, swipe, analytics=None, kb_active=False, active_key=None):
        overlay = img.copy()
        h, w, c = img.shape
        t = time.time()
        
        # Glow color based on state
        glow_color = self.primary_color
        if gesture == "Pinch": glow_color = self.accent_color
        if gesture == "Two-Finger": glow_color = (255, 255, 0) # Yellow for Right Click
        if gesture == "Fist": glow_color = (0, 0, 255)
        
        # 1. Main Dashboard
        cv2.rectangle(overlay, (20, 20), (350, 250), self.bg_panel_color, -1)
        cv2.rectangle(overlay, (20, 20), (350, 250), glow_color, 2)
        
        cv2.putText(overlay, "HCI INTERFACE v3.3", (40, 55), self.font, 0.7, glow_color, 2)
        cv2.line(overlay, (30, 65), (340, 65), glow_color, 1)
        
        # Status & Gesture
        pulse = int(abs(np.sin(t * 3)) * 100 + 155)
        status_color = (0, pulse, 0) if landmarks else (0, 0, pulse)
        cv2.circle(overlay, (45, 95), 8, status_color, -1)
        cv2.putText(overlay, f"SENSORS: {'ONLINE' if landmarks else 'SEARCHING'}", (65, 102), self.font, 0.5, (220, 220, 220), 1)
        cv2.putText(overlay, f"GESTURE: {gesture.upper()}", (40, 140), self.font, 0.6, glow_color, 2)
        cv2.putText(overlay, f"KB MODE: {'ACTIVE' if kb_active else 'OFF'}", (40, 170), self.font, 0.5, self.secondary_color if kb_active else (100, 100, 100), 1)

        # 2. 3D Wireframe (If not in KB mode)
        if not kb_active:
            cube_points = np.array([[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1]])
            cube_center = (landmarks[9][1], landmarks[9][2]) if landmarks else (w-180, h-180)
            cube_scale = 500 + (analytics['pinch_dist']*3 if analytics else 0)
            proj = self._project_3d(cube_points, t*0.4, t*0.2, cube_center, cube_scale)
            for i in range(4):
                cv2.line(overlay, proj[i], proj[(i+1)%4], glow_color, 1)
                cv2.line(overlay, proj[i+4], proj[((i+1)%4)+4], glow_color, 1)
                cv2.line(overlay, proj[i], proj[i+4], glow_color, 1)

        # 3. Analytics
        if analytics:
            p_dist = analytics.get('pinch_dist', 100)
            cv2.rectangle(overlay, (40, 205), (200, 215), (50, 50, 50), -1)
            bar_w = int(np.interp(p_dist, [0, 120], [0, 160]))
            cv2.rectangle(overlay, (40, 205), (40 + bar_w, 215), glow_color, -1)
            cv2.putText(overlay, f"P-DISTANCE: {p_dist}", (40, 200), self.font, 0.4, (200, 200, 200), 1)

        # 5. Targeting Reticle
        if landmarks:
            cursor_pos = analytics['screen_pos'] if analytics else (landmarks[8][1], landmarks[8][2])
            r = 15 + int(np.sin(t * 10) * 5)
            cv2.circle(overlay, cursor_pos, r, glow_color, 2)
            cv2.drawMarker(overlay, cursor_pos, glow_color, cv2.MARKER_CROSS, 25, 1)
            
            if gesture == "Pinch":
                action = "KEY PRESS" if kb_active else "INTERFACE TRIGGER"
                cv2.putText(overlay, action, (cursor_pos[0] + 30, cursor_pos[1]), self.font, 0.6, self.accent_color, 2)
            elif gesture == "Two-Finger":
                cv2.putText(overlay, "RIGHT CLICK", (cursor_pos[0] + 30, cursor_pos[1]), self.font, 0.6, (255,255,0), 2)

        cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
        
        # 6. Overlay Keyboard if active
        if kb_active:
            img = self.draw_keyboard(img, active_key)
            
        return img

        # Composite
        cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
        return img

        # Final Compositing
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        return img
