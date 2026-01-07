import cv2

# カメラを開く
cap = cv2.VideoCapture(0)

# カメラが正常に開かれているか確認
if not cap.isOpened():
    print("カメラが開けませんでした")
    exit()

# 露出と明るさを自動調整に戻す
cap.set(cv2.CAP_PROP_BRIGHTNESS, -1)
cap.set(cv2.CAP_PROP_EXPOSURE, -1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # 自動露出を有効にする

# 他の設定も自動に戻したい場合は以下を試す
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
cap.set(cv2.CAP_PROP_AUTO_WB, 1) # 自動ホワイトバランス
# 映像を表示
while True:
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした")
        break

    cv2.imshow("Webcam Feed", frame)

    # qキーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()