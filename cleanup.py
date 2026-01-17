import os
import shutil

files_to_remove = [
    "check_camera.py",
    "iron_man_main.py",
    "LICENSE",
]

dirs_to_remove = [
    "modules",
    "__pycache__"
]

for f in files_to_remove:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed {f}")
    except Exception as e:
        print(f"Error removing {f}: {e}")

for d in dirs_to_remove:
    try:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Removed directory {d}")
    except Exception as e:
        print(f"Error removing {d}: {e}")
