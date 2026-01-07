import cv2

# カメラを開く
cap = cv2.VideoCapture(0)



# ウィンドウ作成
cv2.namedWindow("Camera")
cv2.namedWindow("Controls")

# スライダーのコールバック関数
def nothing(x):
    pass

# スライダー作成（0〜100スケール）
cv2.createTrackbar("Brightness", "Controls", int(settings["Brightness"]*100), 100, nothing)
cv2.createTrackbar("Contrast", "Controls", int(settings["Contrast"]*100), 100, nothing)
cv2.createTrackbar("Saturation", "Controls", int(settings["Saturation"]*100), 100, nothing)
cv2.createTrackbar("Exposure", "Controls", settings["Exposure"]+10, 20, nothing)  # -10〜10を0〜20で扱う
cv2.createTrackbar("Sharpness", "Controls", settings["Sharpness"], 255, nothing)
cv2.createTrackbar("Gain", "Controls", int(settings["Gain"]*100), 100, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラが開けませんでした")
        break

    # スライダー値を取得してカメラに反映
    cap.set(cv2.CAP_PROP_BRIGHTNESS, cv2.getTrackbarPos("Brightness", "Controls") / 100)
    cap.set(cv2.CAP_PROP_CONTRAST, cv2.getTrackbarPos("Contrast", "Controls") / 100)
    cap.set(cv2.CAP_PROP_SATURATION, cv2.getTrackbarPos("Saturation", "Controls") / 100)
    cap.set(cv2.CAP_PROP_EXPOSURE, cv2.getTrackbarPos("Exposure", "Controls") - 10)
    cap.set(cv2.CAP_PROP_SHARPNESS, cv2.getTrackbarPos("Sharpness", "Controls"))
    cap.set(cv2.CAP_PROP_GAIN, cv2.getTrackbarPos("Gain", "Controls") / 100)

    # 映像表示
    cv2.imshow("Camera", frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
