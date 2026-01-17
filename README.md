# HCI Desktop Interface & Analytics 👁️✋

A professional Computer Vision research project bridging the gap between raw video streams and Human-Computer Interaction (HCI). This system implements a workstation-grade interface for touchless system control, 3D object manipulation, and OS-level workflow automation.

## 🚀 System Capabilities

### 1. High-Precision Cursor Mapping
- **Hardware-Level Control**: Uses PyAutoGUI to map hand landmarks directly to the OS cursor.
- **Damping & Smoothing**: Implements a temporal averaging filter to ensure precise interaction without jitter.
- **Dynamic Mapping**: Automatically scales camera coordinates to the local monitor resolution.

### 2. Multi-Dimensional Gesture Suite
- **Input Triggering**: Real-time "Pinch" detection for system clicks (Distance Analytics).
- **Workflow Automation**:
    - **Horizontal Swipe**: Switches between Virtual Desktops (`Ctrl + Win + Left/Right`).
    - **Vertical Swipe**: Toggles active windows via `Alt + Tab`.
- **State Architecture**: Formalized states for Tracking, Interaction, and Locked (Grab) modes.

### 3. Industrial Interaction HUD
- **3D Visualization**: Real-time projection of 3D wireframe geometry mapped to spatial hand coordinates.
- **Minimalist Design**: A workstation-style silver and charcoal interface optimized for professional utility.
- **Face Mesh Integration**: 468-point high-density facial analysis for gaze-aware system response prototypes.

## 🕹️ Control Manual

| Action | Physical Gesture | System Event |
| :--- | :--- | :--- |
| **Move Cursor** | Index Finger Tip Pointing | Mouse Movement |
| **Left Click** | Thumb + Index Pinch | Mouse Click |
| **Shift Desktop** | Fast Horizontal Swipe (L/R) | Ctrl + Win + Arrow |
| **Switch Window** | Fast Vertical Swipe (U/D) | Alt + Tab |
| **Grab 3D Model** | Closed Fist | Model Lock State |

## 🛠️ Tech Stack
- **Python**: Core logic.
- **OpenCV**: Image signal processing.
- **MediaPipe**: AI landmark extraction.
- **PyAutoGUI**: OS-level hardware interaction.
- **NumPy**: Matrix transformations and 3D projection.

## 📦 Run Instructions

1. **Install requirements**:
   ```bash
   pip install opencv-python mediapipe numpy pyautogui
   ```
2. **Launch interface**:
   ```bash
   python main.py
   ```

## 📂 Project Structure
- `main.py`: The orchestrator and AR loop.
- `ARCHITECTURE.md`: Detailed system design and data flow.
- `hand_tracking.py`: MediaPipe Hand Landmark implementation.
- `face_tracking.py`: 468-Point Face Mesh implementation.
- `gesture_recognition.py`: Euclidean distance analytics and logic.
- `hud_renderer.py`: Industrial-grade AR graphics engine.

---
*Developed for HCI Research, Industrial Automation, and Next-Gen Interface Prototyping.*
