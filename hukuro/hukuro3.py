import cv2
import numpy as np

# 面積のしきい値 (環境に応じて調整)
MIN_AREA = 3000
MAX_AREA = 80000

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. グレイスケール変換とぼかし（ノイズ除去）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0) # 5x5のカーネルでぼかす

    # 2. Cannyエッジ検出
    # (low/high_thresholdは特に環境に応じて微調整が必要)
    edged = cv2.Canny(gray, 50, 150) # 50, 150は一般的な閾値

    # 3. 輪郭検出
    # cv2.RETR_EXTERNAL で一番外側の輪郭のみを抽出 (内側のシワは無視される可能性あり)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    
    # 輪郭のフィルタリング
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 面積でフィルタリング
        if area > MIN_AREA and area < MAX_AREA:
            # ポリ袋として検出されたと見なす
            
            # バウンディングボックスを描画
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            cv2.putText(frame, "Semi-transparent Bag Detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            detected = True
            break
            
    if not detected:
        cv2.putText(frame, "No Bag", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)


    cv2.imshow("Detection Frame", frame)
    cv2.imshow("Canny Edges", edged) # 検出に使われているエッジの画像

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()