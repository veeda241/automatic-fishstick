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
        
        # Glow color based on state
        glow_color = self.primary_color
        if gesture == "Pinch": glow_color = self.accent_color
        if gesture == "Fist": glow_color = (0, 0, 255)
        
        # 1. Main Dashboard (Semi-transparent)
        cv2.rectangle(overlay, (20, 20), (350, 220), self.bg_panel_color, -1)
        cv2.rectangle(overlay, (20, 20), (350, 220), glow_color, 2)
        
        cv2.putText(overlay, "HCI INTERFACE v3.2", (40, 55), self.font, 0.7, glow_color, 2)
        cv2.line(overlay, (30, 65), (340, 65), glow_color, 1)
        
        # Tracking Status with "Pulse"
        pulse = int(abs(np.sin(t * 3)) * 100 + 155)
        status_color = (0, pulse, 0) if landmarks else (0, 0, pulse)
        cv2.circle(overlay, (45, 95), 8, status_color, -1)
        cv2.putText(overlay, f"SENSORS: {'ONLINE' if landmarks else 'SEARCHING'}", (65, 102), self.font, 0.5, (220, 220, 220), 1)
        
        # Active Gesture with dynamic highlight
        gesture_text = f"GESTURE: {gesture.upper()}"
        cv2.putText(overlay, gesture_text, (40, 140), self.font, 0.6, glow_color, 2)

        # 2. 3D Wireframe (Improved contrast and scale)
        cube_points = np.array([
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]
        ])
        
        if landmarks:
            cube_center = (landmarks[9][1], landmarks[9][2])
            cube_scale = 500 + (analytics['pinch_dist'] * 3 if analytics else 0)
        else:
            cube_center = (w - 180, h - 180)
            cube_scale = 350
            
        proj = self._project_3d(cube_points, t*0.4, t*0.2, cube_center, cube_scale)
        
        for i in range(4):
            cv2.line(overlay, proj[i], proj[(i+1)%4], glow_color, 1)
            cv2.line(overlay, proj[i+4], proj[((i+1)%4)+4], glow_color, 1)
            cv2.line(overlay, proj[i], proj[i+4], glow_color, 1)

        # 3. Analytics Dashboard (Responsive bars)
        if analytics:
            p_dist = analytics.get('pinch_dist', 100)
            # Distance Gauge with Color transition
            cv2.rectangle(overlay, (40, 175), (200, 185), (50, 50, 50), -1)
            bar_w = int(np.interp(p_dist, [0, 120], [0, 160]))
            cv2.rectangle(overlay, (40, 175), (40 + bar_w, 185), glow_color, -1)
            cv2.putText(overlay, f"P-DISTANCE: {p_dist}", (40, 170), self.font, 0.4, (200, 200, 200), 1)

        # 4. Animated Scanning Grid (Aesthetic)
        grid_y = int((t * 200) % h)
        cv2.line(overlay, (0, grid_y), (w, grid_y), (glow_color[0]//4, glow_color[1]//4, glow_color[2]//4), 1)

        # 5. Targeting Reticle
        if landmarks:
            cursor_pos = analytics['screen_pos'] if analytics else (landmarks[8][1], landmarks[8][2])
            # Animated Reticle
            r = 15 + int(np.sin(t * 10) * 5)
            cv2.circle(overlay, cursor_pos, r, glow_color, 2)
            cv2.drawMarker(overlay, cursor_pos, glow_color, cv2.MARKER_CROSS, 25, 1)
            
            if gesture == "Pinch":
                cv2.putText(overlay, "INTERFACE TRIGGER", (cursor_pos[0] + 30, cursor_pos[1]), self.font, 0.6, self.accent_color, 2)

        # Composite
        cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
        return img

        # Final Compositing
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        return img
