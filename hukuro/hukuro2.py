import cv2
import numpy as np

# 検出したい色（例：青いポリ袋）のHSV範囲を設定
# (この値は実際の照明やポリ袋の色によって調整が必要です)
lower_hsv = np.array([90, 50, 50])  # 青のHSVの下限
upper_hsv = np.array([130, 255, 255]) # 青のHSVの上限

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. BGRをHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2. マスク（特定の色域を抽出）を生成
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # ノイズ除去 (オプション)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 3. 輪郭検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 4. 面積のしきい値でフィルタリング
        # (ポリ袋の最小・最大サイズに応じて調整)
        if area > 1000 and area < 50000: 
            # ポリ袋として検出された
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, "Plastic Bag Detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            detected = True
            break # 最初の検出でループを抜ける
            
    if not detected:
        cv2.putText(frame, "No Plastic Bag", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()