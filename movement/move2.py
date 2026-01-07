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

# 3. 軌跡を保存するためのキューを初期化
# dequeは効率的に要素の追加・削除ができるデータ構造
# ここでは、各動体の中心座標を保存する辞書
object_trails = {}
max_trail_length = 50  # 軌跡の長さ（点数）

# 4. 物体にIDを割り当てるためのカウンター
object_id_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 5. 背景差分を適用して前景マスクを取得
    fg_mask = bg_subtractor.apply(frame)

    # ノイズ除去
    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 6. 輪郭を検出
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_centers = {}
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        # 7. 輪郭の中心座標を計算
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            center = (cx, cy)
            
            # 8. 既存の物体と照合し、同じ物体かどうかを判断
            # 簡素化のため、最も近い物体を探す
            min_dist = float('inf')
            match_id = -1
            for obj_id, trail in object_trails.items():
                if len(trail) > 0:
                    last_point = trail[-1]
                    dist = np.sqrt((last_point[0] - cx)**2 + (last_point[1] - cy)**2)
                    if dist < min_dist and dist < 100:  # 距離が近い場合のみマッチとみなす
                        min_dist = dist
                        match_id = obj_id
            
            if match_id != -1:
                # 既存の物体を更新
                current_id = match_id
            else:
                # 新しい物体として登録
                current_id = object_id_counter
                object_id_counter += 1
                object_trails[current_id] = deque(maxlen=max_trail_length)
            
            # 9. 軌跡のキューに中心点を追加
            object_trails[current_id].appendleft(center)
            current_centers[current_id] = center

    # 10. 古くなった物体の軌跡を削除
    # 今回検出されなかった物体を特定し、軌跡を消していく
    to_delete = [obj_id for obj_id in object_trails if obj_id not in current_centers]
    for obj_id in to_delete:
        del object_trails[obj_id]

    # 11. 軌跡の描画
    for obj_id, trail in object_trails.items():
        if len(trail) > 1:
            for i in range(1, len(trail)):
                # 古い点ほど薄く、新しい点ほど濃くなるように色を調整
                alpha = (len(trail) - i) / len(trail)
                color = (int(0 * alpha + 255 * (1 - alpha)), int(255 * alpha), 0)
                thickness = int(np.sqrt(max_trail_length / float(i + 1)) * 2)
                cv2.line(frame, trail[i-1], trail[i], color, thickness)
        
        # 現在の中心点に円を描画
        if len(trail) > 0:
            current_point = trail[0]
            cv2.circle(frame, current_point, 10, (0, 255, 255), -1)
            cv2.putText(frame, f"ID: {obj_id}", (current_point[0] + 15, current_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)


    # 12. 結果の表示
    cv2.imshow('Real-time Object Trail Tracking', frame)
    cv2.imshow('Foreground Mask', fg_mask)

    # 'q'キーが押されたら終了
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# 13. 後処理
cap.release()
cv2.destroyAllWindows()