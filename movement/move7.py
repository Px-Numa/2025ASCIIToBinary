import cv2
import numpy as np
import time

# 軌跡を保存するリスト。要素は (中心座標, タイムスタンプ)
# グローバル変数として宣言
trajectory = []

# 軌跡の保持時間 (秒)
TRAJECTORY_LIFETIME = 5

def main():
    # main関数内でグローバル変数'trajectory'を使用することを明示
    global trajectory 

    # カメラからの映像を取得
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("カメラを開けませんでした。")
        return

    # 背景差分オブジェクトを作成 (MOG2アルゴリズムを使用)
    backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 映像を反転させる (手元で試す際に便利)
        # frame = cv2.flip(frame, 1)

        # 背景差分を適用して前景マスクを作成
        fgMask = backSub.apply(frame)

        # ノイズ除去と膨張処理
        kernel = np.ones((5,5),np.uint8)
        opening = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel, iterations = 2)
        dilation = cv2.dilate(opening, kernel, iterations=2)

        # 輪郭を検出
        contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 輪郭が存在する場合
        if contours:
            # 最も面積が大きい輪郭を見つける
            max_contour = max(contours, key=cv2.contourArea)

            # 輪郭の面積が一定のしきい値を超える場合のみ処理 (ノイズ対策)
            if cv2.contourArea(max_contour) > 500:
                # 外接矩形を計算
                x, y, w, h = cv2.boundingRect(max_contour)
                
                # 中心座標を計算
                center_x = x + w // 2
                center_y = y + h // 2

                # 現在のタイムスタンプを取得
                current_time = time.time()

                # 軌跡リストに現在の中心座標とタイムスタンプを追加
                trajectory.append(((center_x, center_y), current_time))

                # バウンディングボックスと中心点を描画
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        # 5秒以上前の古い軌跡を削除
        current_time = time.time()
        # リスト内包表記で条件に合う要素だけを残す
        trajectory = [item for item in trajectory if current_time - item[1] < TRAJECTORY_LIFETIME]

        # 軌跡を描画
        if len(trajectory) > 1:
            for i in range(1, len(trajectory)):
                # 軌跡の点を結んで線を描画
                start_point = trajectory[i-1][0]
                end_point = trajectory[i][0]
                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
        
        # 結果を表示
        cv2.imshow('Tracking Result', frame)
        # cv2.imshow('Foreground Mask', fgMask) # デバッグ用

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()