import pyautogui

# ======================== CONFIGURATION ========================
# These will be updated dynamically based on camera's native resolution
wCam, hCam = 1280, 720  # Default, will be updated
frameR = 100
smoothening = 3  # Lower = faster mouse movement

wScr, hScr = pyautogui.size()

def set_resolution(width, height):
    """Update the global resolution values based on camera detection."""
    global wCam, hCam
    wCam = width
    hCam = height

# ======================== COLORS ========================
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_CYAN = (255, 255, 0)
NEON_ORANGE = (0, 165, 255)
NEON_BLUE = (255, 100, 100)
NEON_RED = (0, 0, 255)
NEON_YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Drawing colors palette
DRAW_COLORS = [NEON_PINK, NEON_GREEN, NEON_CYAN, NEON_ORANGE, NEON_RED, NEON_YELLOW, WHITE]
COLOR_NAMES = ["Pink", "Green", "Cyan", "Orange", "Red", "Yellow", "White"]
