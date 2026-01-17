# HCI Desktop Interface & Analytics v3.3 👁️✋

A professional Computer Vision research project bridging the gap between raw video streams and Human-Computer Interaction (HCI). Version 3.3 introduces **Multi-Finger Interaction** and an **AR Virtual Keyboard**.

## 🚀 System Capabilities

### 1. Multi-Dimensional Gesture Suite
- **Primary Input**: Pinch (Thumb + Index) for Left Click or Key Press.
- **Secondary Input**: **Two-Finger (Index + Middle tips)** for Right Click.
- **Workflow Automation**:
    - **Horizontal Swipe**: Switches between Virtual Desktops (`Ctrl + Win + Left/Right`).
    - **Vertical Swipe**: Toggles active windows via `Alt + Tab`.

### 2. AR Virtual Keyboard
- **Interactive Layout**: Standard QWERTY layout rendered in AR.
- **Precision Targeting**: Hover over keys to highlight them; Pinch to input the character.
- **Toggle Mode**: Use the 'K' key to enable/disable the AR keyboard overlay.

### 3. Industrial Interaction HUD
- **Real-time 3D**: Wireframe projection mapped to spatial hand coordinates.
- **Pulse Feedback**: Dynamic UI glow that responds to gesture detection.
- **Face Mesh Integration**: 468-point analysis for gaze-aware prototype development.

## 🕹️ Control Manual

| Action | Physical Gesture | System Event |
| :--- | :--- | :--- |
| **Move Cursor** | Index Finger Tip Pointing | Mouse Movement |
| **Left Click** | Thumb + Index Pinch | Mouse Click |
| **Right Click** | Index + Middle Tips Close | Mouse Right Click |
| **Type Key** | Hover over AR key + Pinch | Keyboard Input |
| **Shift Desktop** | Fast Horizontal Swipe | Ctrl + Win + Arrow |
| **Switch Window** | Fast Vertical Swipe | Alt + Tab |
| **Grab 3D Model** | Closed Fist | Model Lock State |

## 🛠️ Tech Stack
- **Python**: Core logic.
- **OpenCV**: Image processing.
- **MediaPipe**: AI landmark extraction.
- **PyAutoGUI**: Hardware interaction.
- **NumPy**: Matrix transformations.

## 📦 Run Instructions
1. Install requirements: `pip install opencv-python mediapipe numpy pyautogui`
2. Launch: `python main.py`
3. Toggle Keyboard: Press **'K'** during execution.

---
*Developed for HCI Research, Industrial Automation, and Next-Gen Interface Prototyping.*
