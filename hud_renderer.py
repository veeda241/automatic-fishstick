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

    def draw_hud(self, img, landmarks, face_landmarks, gesture, swipe, analytics=None):
        overlay = img.copy()
        h, w, c = img.shape
        t = time.time()
        
        # 1. Workspace Control Panel (Professional Minimalist)
        cv2.rectangle(overlay, (20, 20), (320, 200), self.bg_panel_color, -1)
        cv2.rectangle(overlay, (20, 20), (320, 200), self.primary_color, 1) # Border
        
        cv2.putText(overlay, "HCI CONTROL INTERFACE", (35, 50), self.font, 0.6, self.primary_color, 1)
        cv2.line(overlay, (35, 60), (300, 60), self.primary_color, 1)
        
        status_color = self.accent_color if landmarks else (0, 0, 255)
        cv2.circle(overlay, (40, 85), 5, status_color, -1)
        cv2.putText(overlay, f"TRACKING: {'LINKED' if landmarks else 'SEARCHING'}", (55, 90), self.font, 0.5, (200, 200, 200), 1)
        cv2.putText(overlay, f"ACTION: {gesture.upper()}", (35, 120), self.font, 0.5, self.secondary_color, 1)

        # 2. 3D Model Interaction (Industrial Design Style)
        cube_points = np.array([
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]
        ])
        
        if landmarks:
            cube_center = (landmarks[9][1], landmarks[9][2])
            cube_scale = 400 + (analytics['pinch_dist'] * 2 if analytics else 0)
        else:
            cube_center = (w - 150, h - 150)
            cube_scale = 300
            
        proj = self._project_3d(cube_points, t*0.3, t*0.5, cube_center, cube_scale)
        
        # Draw 3D Object
        color_3d = self.secondary_color if gesture != "Fist" else (0, 0, 255)
        thickness = 2 if gesture == "Fist" else 1
        for i in range(4):
            cv2.line(overlay, proj[i], proj[(i+1)%4], color_3d, thickness)
            cv2.line(overlay, proj[i+4], proj[((i+1)%4)+4], color_3d, thickness)
            cv2.line(overlay, proj[i], proj[i+4], color_3d, thickness)

        # 3. Analytics Dashboard
        if analytics:
            cv2.putText(overlay, "SIGNAL ANALYTICS", (35, 150), self.font, 0.4, (150, 150, 150), 1)
            p_dist = analytics.get('pinch_dist', 100)
            # Distance Gauge
            cv2.rectangle(overlay, (35, 165), (135, 175), (60, 60, 60), -1)
            bar_w = int(np.interp(p_dist, [0, 100], [0, 100]))
            cv2.rectangle(overlay, (35, 165), (35 + bar_w, 175), self.secondary_color, -1)
            
            # Cursor Coord Display
            cv2.putText(overlay, f"X:{analytics['screen_pos'][0]} Y:{analytics['screen_pos'][1]}", (145, 173), self.font, 0.4, (200, 200, 200), 1)

        # 4. Professional Face Analysis (Minimalist)
        if face_landmarks:
            for face in face_landmarks:
                for id in [33, 133, 362, 263, 1, 61, 291]: # Focus points only
                    cv2.circle(overlay, (face[id][1], face[id][2]), 1, self.primary_color, -1)

        # 5. Interaction Visuals
        if landmarks:
            # Cursor
            cursor_pos = analytics['screen_pos'] if analytics else (landmarks[8][1], landmarks[8][2])
            cv2.circle(overlay, cursor_pos, 12, self.secondary_color, 1)
            cv2.line(overlay, (cursor_pos[0]-15, cursor_pos[1]), (cursor_pos[0]+15, cursor_pos[1]), self.secondary_color, 1)
            cv2.line(overlay, (cursor_pos[0], cursor_pos[1]-15), (cursor_pos[0], cursor_pos[1]+15), self.secondary_color, 1)
            
            if gesture == "Pinch":
                cv2.circle(overlay, cursor_pos, 20, self.accent_color, 2)
                cv2.putText(overlay, "INPUT TRIGGERED", (cursor_pos[0] + 25, cursor_pos[1]), self.font, 0.5, self.accent_color, 1)

        # Final Compositing
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        return img
