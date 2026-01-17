import cv2
import mediapipe as mp
import numpy as np

class FaceTracker:
    def __init__(self, static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.draw_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

    def find_face_mesh(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        
        faces = []
        if self.results.multi_face_landmarks:
            for face_lms in self.results.multi_face_landmarks:
                if draw:
                    # Draw subtle mesh
                    self.mp_draw.draw_landmarks(
                        image=img,
                        landmark_list=face_lms,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_draw.DrawingSpec(color=(255, 200, 0), thickness=1, circle_radius=1)
                    )
                
                face = []
                for id, lm in enumerate(face_lms.landmark):
                    ih, iw, ic = img.shape
                    x, y = int(lm.x * iw), int(lm.y * ih)
                    face.append([id, x, y, lm.z])
                faces.append(face)
                
        return img, faces
