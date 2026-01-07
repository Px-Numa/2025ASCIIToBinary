import cv2

# Webカメラを開く
cap = cv2.VideoCapture(0)

# カメラが正常に開かれたかを確認します。
if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()


# 各種プロパティーの取得
# フレームの幅
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
print(f"Frame Width: {width}")

# フレームの高さ
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Frame Height: {height}")

# フレームレート
frame_rate = cap.get(cv2.CAP_PROP_FPS)
print(f"Frame Rate: {frame_rate}")

# fourcc
fourcc = cap.get(cv2.CAP_PROP_FOURCC)
print(f"FOURCC: {fourcc}")

# フレームデータのフォーマット
format = cap.get(cv2.CAP_PROP_FORMAT)
print(f"Format: {format}")

# 明るさ
brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
print(f"Brightness: {brightness}")

# コントラスト
contrast = cap.get(cv2.CAP_PROP_CONTRAST)
print(f"Contrast: {contrast}")

# 彩度
saturation = cap.get(cv2.CAP_PROP_SATURATION)
print(f"Saturation: {saturation}")

# 色相
hue = cap.get(cv2.CAP_PROP_HUE)
print(f"Hue: {hue}")

# ゲイン
gain = cap.get(cv2.CAP_PROP_GAIN)
print(f"Gain: {gain}")

# 露出
exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
print(f"Exposure: {exposure}")

# オートフォーカスの有効/無効
autofocus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
print(f"Autofocus: {autofocus}")

# 鮮明度
sharpness = cap.get(cv2.CAP_PROP_SHARPNESS)
print(f"Sharpness: {sharpness}")

# ズーム
zoom = cap.get(cv2.CAP_PROP_ZOOM)
print(f"Zoom: {zoom}")

# パン
pan = cap.get(cv2.CAP_PROP_PAN)
print(f"Pan: {pan}")

# チルト
tilt = cap.get(cv2.CAP_PROP_TILT)
print(f"Tilt: {tilt}")

# オート露光
auto_exp = cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
print(f"Auto Exposure: {auto_exp}")


# Webカメラから連続的にフレームをキャプチャ
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # フレームを表示
    cv2.imshow("Small Frame Size: codevace.com", frame)
    
    # 'q'キーを押すとループを終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後片付け
cap.release()
cv2.destroyAllWindows()