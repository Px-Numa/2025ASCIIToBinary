import cv2
import numpy as np

# ----------------------------------------------------------------------
# 定数定義
# ----------------------------------------------------------------------

# 検出対象の白色（発泡スチロール）のHSV範囲を設定
# H: 色相 (Hue), S: 彩度 (Saturation), V: 明度 (Value)
# 白は一般的にSが低く、Vが高い
LOWER_WHITE = np.array([0, 0, 200])    # H: 0, S: 0, V: 200 (暗い白から)
UPPER_WHITE = np.array([180, 50, 255])  # H: 180, S: 50, V: 255 (彩度が低い範囲まで)

# 発泡スチロールとして想定される輪郭の面積範囲 (ピクセル単位)
# この値は、カメラの解像度や対象物との距離によって調整が必要です
MIN_AREA = 50       # これより小さいものはノイズとして無視
MAX_AREA = 5000     # これより大きいものは人や大きなゴミとして無視

# ----------------------------------------------------------------------
# 前処理関数 (提供されたHSV Vチャンネル抽出とガウシアンブラー)
# ----------------------------------------------------------------------
def process_frame_for_mog2(frame):
    # BGRをHSVに変換し、V（Value/明度）チャンネルのみを取り出す
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[:, :, 2]
    # ガウシアンブラーを適用してノイズを平滑化する
    frame = cv2.GaussianBlur(frame, (5, 5), 1)
    return frame

# ----------------------------------------------------------------------
# メイン処理
# ----------------------------------------------------------------------
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False) # 影検出はオフ

# カメラまたは動画ファイルを指定
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

print("発泡スチロール検出を開始します。'q'を押して終了します。")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # ------------------
    # 1. 動きの検出 (MOG2)
    # ------------------
    # MOG2に適用するための前処理フレームを取得
    processed_frame = process_frame_for_mog2(frame.copy())
    
    # MOG2を適用して前景マスクを生成（動いている物体を検出）
    # detectShadowsをFalseにしているため、前景は白(255)、背景は黒(0)
    motion_mask = fgbg.apply(processed_frame)
    
    # ------------------
    # 2. 色の検出 (HSV閾値処理)
    # ------------------
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 設定した白色のHSV範囲に基づき、フレームから白色領域を抽出
    color_mask = cv2.inRange(hsv_frame, LOWER_WHITE, UPPER_WHITE)
    
    # ------------------
    # 3. マスクの結合 (AND演算)
    # ------------------
    # 「動いていて」 かつ 「白い」 領域だけを残す
    combined_mask = cv2.bitwise_and(motion_mask, color_mask)
    
    # ------------------
    # 4. サイズによるフィルタリング
    # ------------------
    # 結合されたマスクに対して輪郭を検出
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 検出された発泡スチロールを描画するためのフレーム（元のフレームのコピー）
    display_frame = frame.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 輪郭の面積が設定した範囲内かチェック
        if MIN_AREA < area < MAX_AREA:
            # 面積条件を満たす場合、それを発泡スチロールとして扱う
            
            # 外接矩形を取得し、元のフレームに描画
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # 緑色の枠
            cv2.putText(display_frame, "Styrofoam", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
    # 結果の表示
    cv2.imshow('1. Original Frame with Detection', display_frame)
    cv2.imshow('2. Motion Mask (MOG2)', motion_mask)
    cv2.imshow('3. Combined Mask (Motion + Color)', combined_mask)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後処理
cap.release()
cv2.destroyAllWindows()