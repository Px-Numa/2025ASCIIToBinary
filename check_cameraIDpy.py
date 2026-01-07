import cv2
import time

def test_index(i):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Windowsなら cv2.CAP_DSHOW 推奨
    if not cap.isOpened():
        return False, None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False, None
    return True, frame

for i in range(0, 10):
    ok, frame = test_index(i)
    if ok:
        print(f"[OK] camera index {i}")
        cv2.imshow(f"camera_{i}", frame)
        cv2.waitKey(1000)  # 1秒表示
        cv2.destroyWindow(f"camera_{i}")
    else:
        print(f"[NO] camera index {i}")