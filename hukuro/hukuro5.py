import cv2

# 背景画像（ポリ袋がない状態）
background_frame = None

cap = cv2.VideoCapture(0)

# 初期背景フレームの取得
print("背景画像をキャプチャしています...")
for _ in range(30): # カメラが安定するまで30フレーム読み捨てる
    ret, frame = cap.read()
    if ret:
        background_frame = frame
        
# 背景をグレイスケールに変換
background_gray = cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
# 背景をぼかしてノイズを減らす
background_gray = cv2.GaussianBlur(background_gray, (21, 21), 0)
print("キャプチャ完了。検出を開始します。")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 現在のフレームを処理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # 1. 背景差分 (現在のフレーム - 背景フレーム)
    frame_delta = cv2.absdiff(background_gray, gray)

    # 2. 閾値処理 (変化があった部分を白にする)
    # (threshの値は照明に応じて調整)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    
    # 穴埋めとノイズ除去
    thresh = cv2.dilate(thresh, None, iterations=2) 
    
    # 3. 輪郭検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 4. 面積のしきい値でフィルタリング
        if area > 1500: # 変化した領域が一定以上であれば検出とする
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Plastic Bag Detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            detected = True
            break
            
    if not detected:
        cv2.putText(frame, "No Plastic Bag", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Detection", frame)
    cv2.imshow("Threshold", thresh) # 検出に使われている変化の画像

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()