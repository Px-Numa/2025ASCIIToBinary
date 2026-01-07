import cv2
import numpy as np
from collections import deque
import math # mathモジュールを追加

# 1. カメラのキャプチャを開始
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()

# 2. 背景差分オブジェクトの生成
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# 3. 軌跡を保存するためのキュー
# object_trailsのdequeには、(x, y, 判定結果) を保存するように変更
object_trails = {} 
max_trail_length = 50

# 4. 物体にIDを割り当てるためのカウンター
object_id_counter = 0

# --- 判定のための定数 ---
# 速度の閾値 (例: 1フレームあたり5ピクセル未満なら遅すぎると判定)
MIN_SPEED_THRESHOLD = 5 
# 直線性の閾値 (例: 過去5フレームの移動方向の平均角度からのずれが30度以上なら斜めと判定)
MAX_ANGLE_DIFF = math.radians(30) # ラジアンに変換
TRAIL_CHECK_LENGTH = 5 # 直線性を判定するための過去フレーム数

def get_angle(p1, p2):
    """2点間の角度（ラジアン）を計算"""
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 5. HSV色空間に変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 6. 白色の範囲を定義し、マスクを作成
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 25, 255])
    color_mask = cv2.inRange(hsv, lower_white, upper_white)

    # 7. 背景差分マスクを取得
    fg_mask = bg_subtractor.apply(frame)

    # 8. 背景差分マスクと色マスクをAND演算で合成
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
                    # trail[-1]は (x, y, 判定結果) のタプルなので、座標のみ取得
                    last_point = trail[0][:2] 
                    dist = np.sqrt((last_point[0] - cx)**2 + (last_point[1] - cy)**2)
                    if dist < min_dist and dist < 100:
                        min_dist = dist
                        match_id = obj_id
            
            # --- 追跡IDの決定 ---
            if match_id != -1:
                current_id = match_id
            else:
                current_id = object_id_counter
                object_id_counter += 1
                object_trails[current_id] = deque(maxlen=max_trail_length)
            
            # --- 速度と直線性の判定 ---
            is_abnormal = False
            
            trail_deque = object_trails[current_id]

            # 速度判定
            current_speed = min_dist # 1フレーム前の位置との距離を速度とする
            if current_speed < MIN_SPEED_THRESHOLD and len(trail_deque) > 0:
                 # 止まっているか、非常に遅い場合は異常
                is_abnormal = True

            # 直線性判定 (十分なデータがある場合のみ)
            if len(trail_deque) >= TRAIL_CHECK_LENGTH:
                angles = []
                for i in range(1, TRAIL_CHECK_LENGTH):
                    p_current = trail_deque[0][:2]
                    p_prev = trail_deque[i][:2]
                    # 座標が全く同じ場合を避ける
                    if p_current[0] != p_prev[0] or p_current[1] != p_prev[1]:
                        angles.append(get_angle(p_prev, p_current))
                
                if len(angles) > 1:
                    # 平均角度からのずれをチェック
                    avg_angle = sum(angles) / len(angles)
                    for angle in angles:
                        angle_diff = abs(angle - avg_angle)
                        # 角度は-πからπまでなので、πを超えたずれを調整
                        if angle_diff > math.pi:
                            angle_diff = 2 * math.pi - angle_diff
                        
                        if angle_diff > MAX_ANGLE_DIFF:
                            is_abnormal = True
                            break
            
            status = "異常" if is_abnormal else "正常"

            # 軌跡に中心座標と判定結果を保存
            object_trails[current_id].appendleft((center[0], center[1], status))
            current_centers[current_id] = center

    # 13. 古い軌跡を削除
    to_delete = [obj_id for obj_id in object_trails if obj_id not in current_centers]
    for obj_id in to_delete:
        del object_trails[obj_id]

    # 14. 軌跡の描画
    for obj_id, trail in object_trails.items():
        if len(trail) > 1:
            for i in range(1, len(trail)):
                # trailの要素は (x, y, status)
                p1 = trail[i-1][:2] 
                p2 = trail[i][:2]
                status = trail[i-1][2] # 直前のフレームでの判定結果
                
                # 判定結果に応じて色を変更
                if status == "異常":
                    line_color = (0, 0, 255) # 赤色
                else:
                    line_color = (0, 255, 0) # 緑色
                
                thickness = int(np.sqrt(max_trail_length / float(i + 1)) * 2)
                cv2.line(frame, p1, p2, line_color, thickness)
        
        if len(trail) > 0:
            current_point = trail[0][:2]
            current_status = trail[0][2]
            
            # 現在の判定結果に基づいて円の色とテキストを設定
            if current_status == "異常":
                circle_color = (0, 0, 255) # 赤色
                text_color = (0, 0, 255)
            else:
                circle_color = (0, 255, 0) # 緑色
                text_color = (0, 255, 0)
            
            cv2.circle(frame, current_point, 10, circle_color, -1)
            
            # IDと判定結果を表示
            display_text = f"ID:{obj_id} {current_status}"
            cv2.putText(frame, display_text, (current_point[0] + 15, current_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    # 15. 結果の表示
    cv2.imshow('Styrofoam Trail Tracking', frame)
    cv2.imshow('Combined Mask', combined_mask)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# 16. 後処理
cap.release()
cv2.destroyAllWindows()