import cv2
import random
import time
from .config import *
from .utils import get_distance

# ======================== SNAKE GAME ========================
snake_body = []
snake_direction = (1, 0)  # Right
food_pos = None
snake_score = 0
game_over = False
snake_speed = 8  # Lower = faster

def init_snake():
    global snake_body, snake_direction, food_pos, snake_score, game_over
    snake_body = [(wCam//2, hCam//2)]
    for i in range(1, 5):
        snake_body.append((wCam//2 - i*20, hCam//2))
    snake_direction = (1, 0)
    spawn_food()
    snake_score = 0
    game_over = False

def spawn_food():
    global food_pos
    food_pos = (random.randint(100, wCam - 100), random.randint(100, hCam - 100))

def snake_game_mode(img, landmarks, fingers, finger_count, frame_count):
    global snake_body, snake_direction, food_pos, snake_score, game_over
    
    if game_over:
        cv2.putText(img, "GAME OVER!", (wCam//2 - 150, hCam//2 - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, NEON_RED, 4)
        cv2.putText(img, f"Score: {snake_score}", (wCam//2 - 80, hCam//2 + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
        cv2.putText(img, "Show 5 fingers to restart", (wCam//2 - 180, hCam//2 + 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, NEON_GREEN, 2)
        
        if finger_count == 5:
            init_snake()
        return
    
    # Control direction with hand position
    index_tip = landmarks[8]
    head = snake_body[0]
    
    # Calculate direction based on finger position relative to snake head
    dx = index_tip[0] - head[0]
    dy = index_tip[1] - head[1]
    
    if abs(dx) > abs(dy):
        new_dir = (1, 0) if dx > 0 else (-1, 0)
    else:
        new_dir = (0, 1) if dy > 0 else (0, -1)
    
    # Prevent 180-degree turns
    if (new_dir[0] != -snake_direction[0] or new_dir[1] != -snake_direction[1]):
        snake_direction = new_dir
    
    # Move snake (slower based on snake_speed)
    if frame_count % snake_speed == 0:
        new_head = (head[0] + snake_direction[0] * 20, head[1] + snake_direction[1] * 20)
        
        # Check wall collision
        if new_head[0] < 50 or new_head[0] > wCam - 50 or new_head[1] < 50 or new_head[1] > hCam - 50:
            game_over = True
            return
        
        # Check self collision
        if new_head in snake_body[1:]:
            game_over = True
            return
        
        snake_body.insert(0, new_head)
        
        # Check food collision
        if get_distance(new_head, food_pos) < 30:
            snake_score += 10
            spawn_food()
        else:
            snake_body.pop()
    
    # Draw game border
    cv2.rectangle(img, (50, 50), (wCam - 50, hCam - 50), NEON_CYAN, 3)
    
    # Draw food
    cv2.circle(img, food_pos, 15, NEON_RED, -1)
    cv2.circle(img, food_pos, 20, NEON_RED, 2)
    
    # Draw snake
    for i, segment in enumerate(snake_body):
        color = NEON_GREEN if i == 0 else (0, 200, 0)
        size = 15 if i == 0 else 12
        cv2.circle(img, segment, size, color, -1)
    
    # Draw pointer (finger position)
    cv2.circle(img, index_tip, 10, NEON_PINK, -1)
    cv2.line(img, head, index_tip, NEON_PINK, 2)
    
    # Score
    cv2.putText(img, f"SNAKE GAME | Score: {snake_score}", (wCam//2 - 150, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, NEON_GREEN, 2)
    cv2.putText(img, "Point where you want the snake to go!", (wCam//2 - 200, hCam - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
