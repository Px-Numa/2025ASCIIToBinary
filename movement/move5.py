import cv2
import numpy as np

# ノイズを減らすためのHSV処理（前処理）
def process_frame(frame):
    # BGRをHSVに変換し、V（Value/明度）チャンネルのみを取り出す
    # これにより、色情報の影響を排除し、明るさの変化に注目する
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[:, :, 2]
    # ガウシアンブラーを適用してノイズを平滑化する
    frame = cv2.GaussianBlur(frame, (5, 5), 1)
    return frame

# ----------------------------------------------------------------------
# メイン処理
# ----------------------------------------------------------------------

# MOG2背景差分器の初期化
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# 例としてカメラまたは動画ファイルを指定
# 例: cap = cv2.VideoCapture(0) # カメラの場合
# 例: cap = cv2.VideoCapture('input_video.mp4') # 動画ファイルの場合
cap = cv2.VideoCapture(0) # 0番のカメラを使用

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

print("MOG2背景差分を開始します。'q'を押して終了します。")

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    # 1. ノイズを減らすための前処理をフレームに適用
    processed_frame = process_frame(frame)
    
    # 2. MOG2アルゴリズムを前処理されたフレームに適用して前景マスクを生成
    #    MOG2は内部でモデルを更新していく
    fgmask = fgbg.apply(processed_frame)
    
    # 3. 影の除去
    #    前景マスクの中で、純粋な前景（255）ではないすべてのピクセルを背景（0）に変更する
    #    これにより、影（通常は灰色/127）が除去される
    fgmask[fgmask != 255] = 0
    
    # 結果の表示
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Foreground Mask (MOG2 + Shadow Removal)', fgmask)
    
    # 'q'が押されたらループを終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後処理
cap.release()
cv2.destroyAllWindows()