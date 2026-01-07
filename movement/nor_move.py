import cv2
import numpy as np

# 1. カメラのキャプチャを開始
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()

# 2. 背景差分オブジェクトの生成
# MOG2は影にも対応しており、比較的安定しています。
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 3. 背景差分を適用して前景マスク（動いている物体）を取得
    fg_mask = bg_subtractor.apply(frame)

    # 4. ノイズ除去（必要に応じて）
    # モルフォロジー変換で小さなノイズを取り除き、物体の穴を埋める
    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 5. 輪郭を検出して物体を特定
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 輪郭の面積が小さすぎる場合はノイズとみなしスキップ
        if cv2.contourArea(contour) < 500:
            continue

        # 輪郭を囲む外接矩形を取得
        x, y, w, h = cv2.boundingRect(contour)

        # 矩形を元のフレームに描画
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 6. 結果の表示
    cv2.imshow('Real-time Object Detection', frame)
    cv2.imshow('Foreground Mask', fg_mask)

    # 'q'キーが押されたら終了
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# 7. 後処理
cap.release()
cv2.destroyAllWindows()

