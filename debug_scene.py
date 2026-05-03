"""Quick test - auto_video_creator directly"""
import sys
sys.path.insert(0, '.')

# Test single scene
from auto_video_creator import make_scene
from pathlib import Path
Path("assets/debug").mkdir(parents=True, exist_ok=True)

print("Testing make_scene...")
result = make_scene(None, "Dhoni ne kiya kuch aisa", 5, "assets/debug/final_test.mp4", idx=0)
print(f"Result: {'✅ SUCCESS' if result else '❌ FAIL'}")

import os
if os.path.exists("assets/debug/final_test.mp4"):
    size = os.path.getsize("assets/debug/final_test.mp4")
    print(f"File size: {size} bytes")