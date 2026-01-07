import cv2
import numpy as np
import time

# --- 設定パラメータ ---
CM_PER_PIXEL = 0.2
MIN_CONTOUR_AREA = 2000 # ★修正: 最小面積を緩和 (5000 → 2000)
MAX_CONTOUR_AREA = 50000 

# 正常性チェックの閾値 (変更なし)
MAX_SPEED_THRESHOLD = 30 / CM_PER_PIXEL
MAX_ROTATION_THRESHOLD = 5
MAX_STUCK_TIME = 1.0
MIN_SEPARATION_DISTANCE = 20 / CM_PER_PIXEL

# 白色検出の閾値 (HSV色空間: H, S, V)
# ★修正: 検出範囲を緩和 (S: 50→80, V: 200→180)
LOWER_WHITE = np.array([0, 0, 180])    # Vの下限を下げた (少し暗い白色も検出)
UPPER_WHITE = np.array([180, 80, 255]) # Sの上限を上げた (少し色がついた白色も検出)

# --- 初期設定 ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラを開けません。")
    exit()

backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)
tracked_objects = {}
next_object_id = 0

# --- メインループ ---
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 1. 動体検出
    fgMask = backSub.apply(gray)
    fgMask = cv2.erode(fgMask, None, iterations=1)
    fgMask = cv2.dilate(fgMask, None, iterations=3)

    # 2. 白色検出
    white_mask = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # 3. マスクのAND結合
    combined_mask = cv2.bitwise_and(fgMask, fgMask, mask=white_mask)
    
    # 4. 輪郭の検出
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    current_time = time.time()
    current_detected_objects = []

    # 検出された輪郭の処理（トラッキングとデータ更新）
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_CONTOUR_AREA and area < MAX_CONTOUR_AREA:
            rect = cv2.minAreaRect(contour)
            (x, y), (w, h), angle = rect
            
            # --- トラッキング ---
            best_match_id = -1
            min_dist = float('inf')
            
            for obj_id, obj_data in tracked_objects.items():
                prev_x, prev_y = obj_data['position']
                dist = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                
                # ★修正: トラッキング距離の緩和 (1.5倍から2.0倍に拡大)
                if dist < min_dist and dist < max(w, h) * 2.0: 
                    min_dist = dist
                    best_match_id = obj_id
            
            # マッチングが成功した場合 (追跡中の物体)
            if best_match_id != -1:
                obj_data = tracked_objects[best_match_id]
                
                # 速度計算
                prev_pos = obj_data.get('prev_pos')
                prev_time = obj_data.get('prev_time')
                speed_pixel_sec = 0
                if prev_pos and prev_time:
                    dist_moved = np.sqrt((x - prev_pos[0])**2 + (y - prev_pos[1])**2)
                    time_delta = current_time - prev_time
                    if time_delta > 0:
                        speed_pixel_sec = dist_moved / time_delta
                
                # データ更新
                obj_data['position'] = (x, y)
                obj_data['last_seen'] = current_time
                obj_data['rotation'] = angle
                obj_data['speed'] = speed_pixel_sec
                obj_data['prev_pos'] = (x, y)
                obj_data['prev_time'] = current_time
                obj_data['rect_coords'] = rect
                
                current_detected_objects.append(best_match_id)
            
            # 新しい物体を検出した場合
            else:
                new_id = next_object_id
                tracked_objects[new_id] = {
                    'position': (x, y),
                    'last_seen': current_time,
                    'rotation': angle,
                    'speed': 0,
                    'prev_pos': (x, y),
                    'prev_time': current_time,
                    'status': 'OK',
                    'rect_coords': rect
                }
                current_detected_objects.append(new_id)
                next_object_id += 1

    # --- 異常検知ロジックと結果表示 ---
    for obj_id, obj_data in tracked_objects.items():
        if obj_id not in current_detected_objects:
            continue
        
        position = obj_data['position']
        speed = obj_data['speed']
        rotation = obj_data['rotation']
        status = 'OK'
        
        # 速度チェック
        if speed * CM_PER_PIXEL > MAX_SPEED_THRESHOLD:
            status = 'ERROR (速度超過)'
        elif current_time - obj_data['last_seen'] > MAX_STUCK_TIME and speed * CM_PER_PIXEL < 1:
            status = 'ERROR (詰まり)'
            
        # 傾きチェック
        if abs(rotation) > MAX_ROTATION_THRESHOLD and abs(rotation - 90) > MAX_ROTATION_THRESHOLD:
            status = 'ERROR (傾き)'
            
        # 隣接チェック
        for other_id, other_data in tracked_objects.items():
            if obj_id != other_id and other_id in current_detected_objects:
                dist = np.sqrt((position[0] - other_data['position'][0])**2 + (position[1] - other_data['position'][1])**2)
                if dist < MIN_SEPARATION_DISTANCE:
                    status = 'ERROR (詰まり：近すぎ)'
                    break
        
        obj_data['status'] = status
        
        # 結果の表示
        rect_coords = obj_data.get('rect_coords')
        if rect_coords:
            box = cv2.boxPoints(rect_coords)
            box = np.int0(box)
            
            color = (0, 255, 0) if status == 'OK' else (0, 0, 255)
            cv2.drawContours(frame, [box], 0, color, 2)
            cv2.putText(frame, f"Set {obj_id}: {status}", (int(position[0]) - 50, int(position[1]) - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, f"Speed: {speed * CM_PER_PIXEL:.2f} cm/s", (int(position[0]) - 50, int(position[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, f"Rot: {rotation:.1f} deg", (int(position[0]) - 50, int(position[1]) + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
    # 古い追跡対象を削除
    tracked_objects = {obj_id: obj_data for obj_id, obj_data in tracked_objects.items() if obj_data['last_seen'] > current_time - 2.0}

    cv2.imshow("Tracking (White & Moving)", frame)
    cv2.imshow("Combined Mask", combined_mask) 
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()