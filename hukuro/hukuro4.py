import cv2
import numpy as np

# ***** 調整ポイント1: 面積のしきい値 *****
# 検出されない場合、まずMIN_AREAを下げて、大きなノイズも検出されるか確認します。
# この画像（1280x720と仮定）の場合、10000では大きすぎる可能性があります。
MIN_AREA = 5000  # 10000から5000に下げてみる
MAX_AREA = 100000 

# ***** 調整ポイント2: Cannyの閾値 *****
# 検出されない主な原因です。low_thresholdを下げて感度を上げます。
# high_thresholdもlow_thresholdの2〜3倍程度に保ちます。
CANNY_LOW_THRESHOLD = 30 # 50から30に下げる
CANNY_HIGH_THRESHOLD = 90 # 150から90に下げる

cap = cv2.VideoCapture(0)

# (カメラ初期化と解像度表示の省略)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. グレイスケール変換とぼかし
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0) # ぼかしを少し強く (7x7) してノイズを減らす

    # 2. Cannyエッジ検出 (調整した閾値を適用)
    edged = cv2.Canny(gray, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD) 

    # 3. 輪郭検出
    # RETR_EXTERNAL で外側の輪郭のみを抽出
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 4. 面積でフィルタリング (調整したMIN_AREA, MAX_AREAを適用)
        if area > MIN_AREA and area < MAX_AREA:
            
            # 💡 フィルタリングの追加: 縦横比の確認
            # 非常に細長いノイズを除外するため、縦横比（アスペクト比）も確認
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # 例えば、縦横比が 0.1〜10 の範囲にあるもののみを対象とする
            if 0.1 < aspect_ratio < 10.0:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, f"Bag Detected (Area: {area:.0f})", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                detected = True
                break
            
    if not detected:
        cv2.putText(frame, "No Large Bag", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    cv2.imshow("Detection Frame", frame)
    cv2.imshow("Canny Edges (Check if contour is closed)", edged) # エッジ画像を確認しながら調整！

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()