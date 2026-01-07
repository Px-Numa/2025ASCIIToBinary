import cv2

# カメラを開く
cap = cv2.VideoCapture(0)

# 設定値（HD画質 + 自然な見え方 + 自動露出/オートフォーカス調整）
settings = {
    cv2.CAP_PROP_FRAME_WIDTH: 1280,
    cv2.CAP_PROP_FRAME_HEIGHT: 720,
    cv2.CAP_PROP_FPS: 30,
    cv2.CAP_PROP_BRIGHTNESS: 0.5,      # 0〜1の範囲の場合
    cv2.CAP_PROP_CONTRAST: 0.5,        # 0〜1の範囲の場合
    cv2.CAP_PROP_SATURATION: 0.55,     # 0.5〜0.6程度
    cv2.CAP_PROP_EXPOSURE: -4,         # 負の値で露出調整
    cv2.CAP_PROP_AUTOFOCUS: 1          # ON
}

# 設定を適用
for prop, value in settings.items():
    cap.set(prop, value)

# 設定が反映されたか確認
print("=== Current Camera Properties ===")
for prop, value in settings.items():
    print(f"{prop}: {cap.get(prop)}")

# 映像を表示
while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラが開けませんでした")
        break

    cv2.imshow("HD Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
