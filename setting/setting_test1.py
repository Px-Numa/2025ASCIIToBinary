import cv2

# カメラを開く
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラが開けませんでした")
    exit()

# 指定設定
custom_settings = {
    cv2.CAP_PROP_FRAME_WIDTH: 640.0,
    cv2.CAP_PROP_FRAME_HEIGHT: 480.0,
    cv2.CAP_PROP_FPS: 30.0,
    cv2.CAP_PROP_BRIGHTNESS: 70.0,
    cv2.CAP_PROP_CONTRAST: 129.0,
    cv2.CAP_PROP_SATURATION: 128.0,
    cv2.CAP_PROP_HUE: 103.0,
    cv2.CAP_PROP_GAIN: 0.0,
    cv2.CAP_PROP_EXPOSURE: -3.0,
    cv2.CAP_PROP_AUTOFOCUS: 0.0,
    cv2.CAP_PROP_SHARPNESS: 240.0,
    cv2.CAP_PROP_ZOOM: -1.0,
    cv2.CAP_PROP_AUTO_EXPOSURE: 0.0
}

# 設定を適用
for prop, value in custom_settings.items():
    cap.set(prop, value)

# 設定確認
print("=== Current Camera Properties ===")
for prop, value in custom_settings.items():
    print(f"{prop}: {cap.get(prop)}")

# 映像表示
while True:
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした")
        break

    cv2.imshow("Custom Camera Settings", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

