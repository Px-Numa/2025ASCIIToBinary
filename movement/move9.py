import cv2
import numpy as np

# --- 1. 定数と初期設定 ---
# HSV色空間で白色を定義（環境光や影に応じて調整が必要です！）
# H: 色相(0-180), S: 彩度(0-255), V: 明度(0-255)
# 影の影響を考慮し、V_minを低めに、背景ノイズを避けるためS_maxを低めに設定
LOWER_WHITE = np.array([0, 0, 150])    # 比較的暗い白まで許容（影対策）
UPPER_WHITE = np.array([180, 70, 255]) # 彩度が高いもの（色がついたもの）は無視

# 追跡された重心座標を保存するリスト
trajectory = []

# 平滑化された軌跡を保存するリスト（直進性判定に使用）
smoothed_trajectory = [] 

# 移動平均フィルターのウィンドウサイズ
SMOOTHING_WINDOW_SIZE = 5 

# 直線判定を始めるために必要な平滑化された点数
MIN_POINTS_FOR_LINE = 50 

# 直進性の判定に使う許容ズレ閾値 (ピクセル単位)。調整が必要！
MAX_DEVIATION_THRESHOLD = 20 
# (例: 10だと非常に厳格、30だと緩やか)

# --- 2. 理想的な直線の計算関数 ---
def get_ideal_line(points):
    """
    点のリストに最小二乗法で直線をフィットさせ、その傾きと切片を返す。
    """
    if len(points) < 2:
        return None, None

    x_coords = np.array([p[0] for p in points])
    y_coords = np.array([p[1] for p in points])

    # 最小二乗法で直線 (y = m*x + b) を計算
    try:
        m, b = np.polyfit(x_coords, y_coords, 1)
        return m, b
    except np.linalg.LinAlgError:
        # データが垂直線に近いなど、計算できない場合
        return None, None

# --- 3. メイン処理 ---
def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("エラー: Webカメラが見つかりません。カメラ番号を確認してください。")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        H, W, _ = frame.shape
        center_x, center_y = None, None
        is_straight = True
        current_deviation = 0.0

        # 1. HSV色空間に変換
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. マスクの作成 (白色の抽出)
        mask = cv2.inRange(hsv_frame, LOWER_WHITE, UPPER_WHITE)
        
        # 3. ノイズ除去（モルフォロジー演算で精度向上）
        kernel_open = np.ones((7, 7), np.uint8)
        kernel_close = np.ones((9, 9), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)

        # 4. 輪郭の検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 最も大きい輪郭を見つけて発泡スチロールとする
        if contours:
            c = max(contours, key=cv2.contourArea)
            
            # 輪郭の面積が小さすぎる（ノイズと判断）場合は無視
            if cv2.contourArea(c) > 500: # 面積閾値は発泡スチロールの大きさに応じて調整
                
                # 重心（モーメント）を計算
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    
                    # 5. 生の座標をリストに追加
                    trajectory.append((center_x, center_y))

                    # 6. 移動平均フィルターを適用して位置を平滑化
                    if len(trajectory) >= SMOOTHING_WINDOW_SIZE:
                        # 直近の N フレームの平均を取る
                        avg_x = int(np.mean([p[0] for p in trajectory[-SMOOTHING_WINDOW_SIZE:]]))
                        avg_y = int(np.mean([p[1] for p in trajectory[-SMOOTHING_WINDOW_SIZE:]]))
                        
                        # 平滑化された座標を記録
                        if not smoothed_trajectory or smoothed_trajectory[-1] != (avg_x, avg_y):
                            smoothed_trajectory.append((avg_x, avg_y))
                        
                        current_tracking_point = (avg_x, avg_y)
                    else:
                        current_tracking_point = (center_x, center_y) # 最初の数フレームはそのまま

                    # 輪郭と平滑化された重心を描画
                    cv2.circle(frame, current_tracking_point, 7, (0, 0, 255), -1) # 赤い大きな点
                    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2) # 緑の輪郭線

        
        # 7. 直進性の判定と描画
        if len(smoothed_trajectory) > MIN_POINTS_FOR_LINE:
            
            # 理想的な直線を計算 (平滑化された軌跡を使用)
            m, b = get_ideal_line(smoothed_trajectory)
            
            if m is not None and b is not None:
                # 理想直線を描画
                pt1 = (0, int(b))
                pt2 = (W, int(m * W + b))
                cv2.line(frame, pt1, pt2, (255, 0, 0), 2) # 青い基準線

                # 最新の平滑化された点と直線との距離（ズレ）を計算
                last_x, last_y = smoothed_trajectory[-1]
                
                # 点と直線の距離の公式: |Ax + By + C| / sqrt(A^2 + B^2)
                # m*x - y + b = 0
                current_deviation = abs(m * last_x - last_y + b) / np.sqrt(m**2 + 1)
                
                # ズレが閾値を超えたら「曲がっている」と判定
                if current_deviation > MAX_DEVIATION_THRESHOLD:
                    is_straight = False

            # 判定結果のテキスト表示
            if is_straight:
                status_text = f"直進中 | ズレ: {current_deviation:.1f} px"
                color = (0, 255, 0) # 緑
            else:
                status_text = f"曲がっています！ | ズレ: {current_deviation:.1f} px (閾値: {MAX_DEVIATION_THRESHOLD})"
                color = (0, 0, 255) # 赤
            
            cv2.putText(frame, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # 軌跡（過去の点）を赤で描画 (平滑化された軌跡を使用)
            for i in range(1, len(smoothed_trajectory)):
                cv2.line(frame, smoothed_trajectory[i-1], smoothed_trajectory[i], (0, 0, 255), 1)

        else:
            cv2.putText(frame, f"初期データ収集 ({len(smoothed_trajectory)}/{MIN_POINTS_FOR_LINE})", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


        # 画面表示
        cv2.imshow("Styrofoam Tracking (Result)", frame)
        cv2.imshow("White Mask (For Debug)", mask) # マスク画像を確認用で表示

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()