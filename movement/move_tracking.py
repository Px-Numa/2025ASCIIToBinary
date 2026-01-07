"""
【発泡スチロール異常移動検知システム】

使用技術: Python, OpenCV
画像処理手法:
  - 前処理: 背景差分 (`cv2.BackgroundSubtractorMOG2`)
  - 物体検出: 輪郭抽出 (`cv2.findContours`) と面積フィルタリング
  - 追跡: 検出した物体と過去位置の近傍探索によるマルチオブジェクトトラッキング
検知内容:
  - 速度異常 (移動速度の超過または停止)
  - 詰まり (隣接物体との距離閾値、または速度ゼロが継続)
  - 傾き異常 (物体の回転角度)

# 他の正常移動プログラムとの区別
# このプログラムは、複数の物体を同時に追跡し、速度、傾き、隣接距離の3つの観点から多角的に異常を検知します。

CM_PER_PIXEL: 物体の速度を物理的な単位で計算するために使用します。カメラと対象物の距離やレンズによって変わるので、測定して調整してください。
MIN_CONTOUR_AREAとMAX_CONTOUR_AREA: 誤検出を防ぐため、検出対象のサイズに合わせて調整します。
MAX_SPEED_THRESHOLD: 15cm/sを基準に、許容範囲を設定します。
MAX_ROTATION_THRESHOLD: 傾きの許容範囲を設定します。
MAX_STUCK_TIME: 物体が停止してからエラーと判定するまでの秒数です。
MIN_SEPARATION_DISTANCE: 隣接するセット間の最小距離を設定し、衝突や詰まりを検知します。

速度: 
最新の位置情報と前回の位置情報から速度を計算し、MAX_SPEED_THRESHOLDと比較します。
詰まり:
一定時間（MAX_STUCK_TIME）以上、速度がほぼゼロの場合に「詰まり」と判定します。
他のセットとの距離がMIN_SEPARATION_DISTANCEより小さい場合に「詰まり：近すぎ」と判定します。
傾き: 
輪郭の最小外接矩形から角度を取得し、MAX_ROTATION_THRESHOLDと比較します。
結果表示:
正常な場合は緑色の枠、異常な場合は赤色の枠で囲み、状態情報をテキストで表示します。


"""

import cv2
import numpy as np
import time

# --- 設定パラメータ ---
CM_PER_PIXEL = 0.2  # 物理的な測定に基づく、ピクセルあたりの実寸（cm/pixel）
MIN_CONTOUR_AREA = 5000  # 検出する輪郭の最小面積（発泡スチロールセットのサイズに合わせる）
MAX_CONTOUR_AREA = 50000 # 検出する輪郭の最大面積

# 正常性チェックの閾値
MAX_SPEED_THRESHOLD = 30 / CM_PER_PIXEL  # 異常な速度（pixel/sec）
MAX_ROTATION_THRESHOLD = 5  # 異常な傾き（度）
MAX_STUCK_TIME = 1.0  # 詰まりと判定するまでの時間（秒）
MIN_SEPARATION_DISTANCE = 20 / CM_PER_PIXEL  # 詰まりと判定する隣接セット間の最小距離（pixel）

# --- 初期設定 ---
cap = cv2.VideoCapture(0)  # カメラまたは動画ファイル
if not cap.isOpened():
    print("カメラを開けません。")
    exit()

# 背景差分器の初期化
backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)

# 追跡する物体の情報（ID、位置、最終更新時刻、速度、傾きなど）
tracked_objects = {}
next_object_id = 0

# --- メインループ ---
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 映像をグレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 背景差分の適用
    fgMask = backSub.apply(gray)
    
    # フィルタリング
    fgMask = cv2.erode(fgMask, None, iterations=1)
    fgMask = cv2.dilate(fgMask, None, iterations=3)
    
    # 輪郭の検出
    contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    current_time = time.time()
    current_detected_objects = []

    # 検出された輪郭の処理
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_CONTOUR_AREA and area < MAX_CONTOUR_AREA:
            # 最小外接矩形を計算
            rect = cv2.minAreaRect(contour)
            (x, y), (w, h), angle = rect
            
            # --- トラッキング ---
            best_match_id = -1
            min_dist = float('inf')
            
            # 既存の追跡対象と最も近いものを探す
            for obj_id, obj_data in tracked_objects.items():
                prev_x, prev_y = obj_data['position']
                dist = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                if dist < min_dist:
                    min_dist = dist
                    best_match_id = obj_id
            
            # マッチングが成功した場合
            if best_match_id != -1 and min_dist < max(w, h):
                tracked_objects[best_match_id]['position'] = (x, y)
                tracked_objects[best_match_id]['last_seen'] = current_time
                tracked_objects[best_match_id]['rotation'] = angle
                
                # 速度計算
                prev_pos = tracked_objects[best_match_id].get('prev_pos')
                prev_time = tracked_objects[best_match_id].get('prev_time')
                if prev_pos and prev_time:
                    dist_moved = np.sqrt((x - prev_pos[0])**2 + (y - prev_pos[1])**2)
                    time_delta = current_time - prev_time
                    if time_delta > 0:
                        speed_pixel_sec = dist_moved / time_delta
                        tracked_objects[best_match_id]['speed'] = speed_pixel_sec
                
                tracked_objects[best_match_id]['prev_pos'] = (x, y)
                tracked_objects[best_match_id]['prev_time'] = current_time
                
                current_detected_objects.append(best_match_id)
            
            # 新しい物体を検出した場合
            else:
                tracked_objects[next_object_id] = {
                    'position': (x, y),
                    'last_seen': current_time,
                    'rotation': angle,
                    'speed': 0,
                    'prev_pos': (x, y),
                    'prev_time': current_time,
                    'status': 'OK'
                }
                current_detected_objects.append(next_object_id)
                next_object_id += 1

    # --- 異常検知ロジック ---
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
        elif current_time - obj_data['last_seen'] > MAX_STUCK_TIME and speed < 1:
            status = 'ERROR (詰まり)'
            
        # 傾きチェック
        if abs(rotation) > MAX_ROTATION_THRESHOLD and abs(rotation - 90) > MAX_ROTATION_THRESHOLD:
            status = 'ERROR (傾き)'
            
        # 隣接チェック（詰まり判定）
        for other_id, other_data in tracked_objects.items():
            if obj_id != other_id and other_id in current_detected_objects:
                dist = np.sqrt((position[0] - other_data['position'][0])**2 + (position[1] - other_data['position'][1])**2)
                if dist < MIN_SEPARATION_DISTANCE:
                    status = 'ERROR (詰まり：近すぎ)'
                    break
        
        tracked_objects[obj_id]['status'] = status
        
        # --- 結果の表示 ---
        box = cv2.boxPoints(cv2.minAreaRect(contour))
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

    cv2.imshow("Tracking", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
