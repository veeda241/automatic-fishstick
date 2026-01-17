import numpy as np
import cv2

def count_fingers(landmarks, handedness):
    fingers = []
    if handedness == "Right":
        fingers.append(1 if landmarks[4][0] < landmarks[3][0] else 0)
    else:
        fingers.append(1 if landmarks[4][0] > landmarks[3][0] else 0)
    
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for tip, pip in zip(tips, pips):
        fingers.append(1 if landmarks[tip][1] < landmarks[pip][1] else 0)
    
    return sum(fingers), fingers

def get_distance(p1, p2):
    return int(np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2))

def draw_fancy_box(img, x1, y1, x2, y2, color, thickness=2, corner_length=30):
    cv2.line(img, (x1, y1), (x1 + corner_length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + corner_length), color, thickness)
    cv2.line(img, (x2, y1), (x2 - corner_length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + corner_length), color, thickness)
    cv2.line(img, (x1, y2), (x1 + corner_length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - corner_length), color, thickness)
    cv2.line(img, (x2, y2), (x2 - corner_length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - corner_length), color, thickness)

def draw_button(img, text, x, y, w, h, color, selected=False):
    WHITE = (255, 255, 255)
    thickness = -1 if selected else 2
    cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
    if selected:
        cv2.rectangle(img, (x, y), (x + w, y + h), WHITE, 2)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE if selected else color, 2)
