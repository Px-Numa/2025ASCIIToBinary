import cv2

# カメラを開く
cap = cv2.VideoCapture(0)

# 指定された設定値
custom_settings = {
    cv2.CAP_PROP_FRAME_WIDTH: 640.0,
    cv2.CAP_PROP_FRAME_HEIGHT: 480.0,
    cv2.CAP_PROP_FPS: 30.0,
    cv2.CAP_PROP_FOURCC: 22.0,
    cv2.CAP_PROP_FORMAT: -1.0,
    cv2.CAP_PROP_BRIGHTNESS: 0.0,
    cv2.CAP_PROP_CONTRAST: 32.0,
    cv2.CAP_PROP_SATURATION: 75.0,
    cv2.CAP_PROP_HUE: 0.0,
    cv2.CAP_PROP_GAIN: 0.0,
    cv2.CAP_PROP_EXPOSURE: -6.0,
    cv2.CAP_PROP_AUTOFOCUS: -1.0,
    cv2.CAP_PROP_SHARPNESS: 4.0,
    cv2.CAP_PROP_ZOOM: -1.0,
    cv2.CAP_PROP_PAN: -1.0,
    cv2.CAP_PROP_TILT: -1.0,
    cv2.CAP_PROP_AUTO_EXPOSURE: 0.0
}

# 設定を適用
for prop, value in custom_settings.items():
    cap.set(prop, value)

# 設定が反映されたか確認
print("=== Current Camera Properties ===")
for prop, value in custom_settings.items():
    print(f"{prop}: {cap.get(prop)}")

# 映像を表示
while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラが開けませんでした")
        break

    cv2.imshow("Custom Camera Settings", frame)

    # qキーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
