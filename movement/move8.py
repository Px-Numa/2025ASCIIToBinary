import cv2
import numpy as np

# --- 1. 定数と初期設定 ---
# HSV色空間で白色を定義（環境に応じて調整が必要）
# 白は彩度が低く(S_maxを小さく)、明度が高い(V_minを大きく)
# (H:0-180, S:0-255, V:0-255)
LOWER_WHITE = np.array([0, 0, 200])    # H: 0, S: 0, V: 200 (明るい白)
UPPER_WHITE = np.array([180, 50, 255]) # H: 180, S: 50, V: 255 (彩度が低い部分を白と見なす)

# 追跡された重心座標を保存するリスト
trajectory = []

# 直進性の判定に使う閾値 (ピクセル単位)。この値を超えると「曲がっている」と判定
MAX_DEVIATION_THRESHOLD = 20 # 例: 20ピクセル

# --- 2. 理想的な直線の計算関数 ---
def get_ideal_line(points):
    """
    点のリストに最小二乗法で直線をフィットさせ、その傾きと切片を返す。
    点が少ない場合は None を返す。
    """
    if len(points) < 2:
        return None, None

    x_coords = np.array([p[0] for p in points])
    y_coords = np.array([p[1] for p in points])

    # 最小二乗法で直線 (y = m*x + b) を計算
    # np.polyfitは多項式フィッティングを行う
    try:
        m, b = np.polyfit(x_coords, y_coords, 1)
        return m, b
    except np.linalg.LinAlgError:
        # データが垂直線に近いなど、計算できない場合
        return None, None

# --- 3. メイン処理 ---
def main():
    # Webカメラを開く (0 はデフォルトのカメラ)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("エラー: Webカメラが見つかりません。")
        return

    # 最初の数フレームを使って理想直線を決めるためのフラグ
    # 実際の発泡スチロールの動きが安定してから判定を開始するために使う
    start_tracking_count = 0 
    MIN_POINTS_FOR_LINE = 50 # 直線判定を始めるために必要な点数

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
        
        # オプション: ノイズ除去 (モルフォロジー演算)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 3. 輪郭の検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 最も大きい輪郭を見つけて発泡スチロールとする
        if contours:
            c = max(contours, key=cv2.contourArea)
            
            # 発泡スチロールが小さすぎる場合は無視
            if cv2.contourArea(c) > 100: 
                
                # 重心（モーメント）を計算
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    
                    # 座標をリストに追加
                    trajectory.append((center_x, center_y))

                    # 輪郭と重心を描画
                    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1) # 重心
                    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2) # 輪郭線
        
        # 4. 追跡と直進性の判定
        if len(trajectory) > MIN_POINTS_FOR_LINE:
            
            # 理想的な直線を計算
            m, b = get_ideal_line(trajectory)
            
            if m is not None and b is not None:
                # 理想直線を描画 (画面全体に描画するために端の座標を計算)
                pt1 = (0, int(b))
                pt2 = (W, int(m * W + b))
                cv2.line(frame, pt1, pt2, (255, 0, 0), 2) # 青い線

                # 各フレームでの理想直線からのズレを計算
                # 最後の点（最新の位置）と直線との距離を計算
                last_x, last_y = trajectory[-1]
                
                # 点と直線の距離の公式: |Ax + By + C| / sqrt(A^2 + B^2)
                # y = m*x + b  =>  m*x - y + b = 0
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
            
            # 軌跡（過去の点）を赤で描画
            for i in range(1, len(trajectory)):
                cv2.line(frame, trajectory[i-1], trajectory[i], (0, 0, 255), 1)

        else:
            cv2.putText(frame, f"初期データ収集 ({len(trajectory)}/{MIN_POINTS_FOR_LINE})", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


        # 画面表示
        cv2.imshow("Styrofoam Tracking", frame)
        cv2.imshow("White Mask (For Debug)", mask) # マスク画像を確認用で表示

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()