import cv2
import numpy as np
from collections import deque

# 1. カメラのキャプチャを開始
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()

# 2. 背景差分オブジェクトの生成
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# 3. 軌跡を保存するためのキュー
object_trails = {}
max_trail_length = 50

# 4. 物体にIDを割り当てるためのカウンター
object_id_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 5. HSV色空間に変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 6. 白色の範囲を定義し、マスクを作成
    # 一般的な白色の範囲
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 25, 255])
    
    # 実際の発泡スチロールの色に応じて、この範囲を調整してください
    color_mask = cv2.inRange(hsv, lower_white, upper_white)

    # 7. 背景差分マスクを取得
    fg_mask = bg_subtractor.apply(frame)

    # 8. 背景差分マスクと色マスクをAND演算で合成
    # これにより、「動いていて、かつ白い部分」のみが残る
    combined_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=color_mask)

    # 9. ノイズ除去
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 10. 輪郭を検出
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_centers = {}
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        # 11. 輪郭の中心座標を計算
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            center = (cx, cy)
            
            # 12. 既存の物体と照合
            min_dist = float('inf')
            match_id = -1
            for obj_id, trail in object_trails.items():
                if len(trail) > 0:
                    last_point = trail[-1]
                    dist = np.sqrt((last_point[0] - cx)**2 + (last_point[1] - cy)**2)
                    if dist < min_dist and dist < 100:
                        min_dist = dist
                        match_id = obj_id
            
            if match_id != -1:
                current_id = match_id
            else:
                current_id = object_id_counter
                object_id_counter += 1
                object_trails[current_id] = deque(maxlen=max_trail_length)
            
            object_trails[current_id].appendleft(center)
            current_centers[current_id] = center

    # 13. 古い軌跡を削除
    to_delete = [obj_id for obj_id in object_trails if obj_id not in current_centers]
    for obj_id in to_delete:
        del object_trails[obj_id]

    # 14. 軌跡の描画
    for obj_id, trail in object_trails.items():
        if len(trail) > 1:
            for i in range(1, len(trail)):
                alpha = (len(trail) - i) / len(trail)
                color = (int(0 * alpha + 255 * (1 - alpha)), int(255 * alpha), 0)
                thickness = int(np.sqrt(max_trail_length / float(i + 1)) * 2)
                cv2.line(frame, trail[i-1], trail[i], color, thickness)
        
        if len(trail) > 0:
            current_point = trail[0]
            cv2.circle(frame, current_point, 10, (0, 255, 255), -1)
            cv2.putText(frame, f"ID: {obj_id}", (current_point[0] + 15, current_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # 15. 結果の表示
    cv2.imshow('Styrofoam Trail Tracking', frame)
    cv2.imshow('Combined Mask', combined_mask)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# 16. 後処理
cap.release()
cv2.destroyAllWindows()