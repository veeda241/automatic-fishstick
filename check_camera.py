import cv2

def list_ports():
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return working_ports, available_ports

def check_resolutions():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    resolutions = [
        (1920, 1080), (1280, 720), (800, 600), (640, 480)
    ]
    
    print("\nSupported Resolutions:")
    for w, h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Requested: {w}x{h} -> Actual: {int(actual_w)}x{int(actual_h)}")

    cap.release()

if __name__ == "__main__":
    check_resolutions()
