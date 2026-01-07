import cv2
import os

# 背景画像のファイルパス
background_image_path = "image/image_20251022_14-21-21.png"

# 1. 背景画像をファイルから読み込む
if not os.path.exists(background_image_path):
    print(f"エラー: 背景画像ファイルが見つかりません: {background_image_path}")
    # 処理を停止するか、代替手段を設ける
    exit()

# 画像を読み込む（カラーで読み込む）
background_frame = cv2.imread(background_image_path)

if background_frame is None:
    print(f"エラー: 画像ファイルの読み込みに失敗しました: {background_image_path}")
    exit()

# 背景をグレイスケールに変換
background_gray = cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
# 背景をぼかしてノイズを減らす
background_gray = cv2.GaussianBlur(background_gray, (21, 21), 0)
print(f"背景画像 '{background_image_path}' を読み込み、検出を開始します。")

# 2. カメラの初期化（ライブ映像用）
cap = cv2.VideoCapture(0)

# 背景画像とカメラのフレームサイズが異なる場合の対策（オプション）
# カメラからのフレームサイズを取得
ret, frame_temp = cap.read()
if ret:
    h_cap, w_cap = frame_temp.shape[:2]
    h_bg, w_bg = background_gray.shape[:2]
    
    # サイズが異なる場合は、背景画像をリサイズしてカメラのフレームサイズに合わせる
    if h_cap != h_bg or w_cap != w_bg:
        print(f"警告: 背景画像 ({w_bg}x{h_bg}) とカメラフレーム ({w_cap}x{h_cap}) のサイズが異なります。背景画像をリサイズします。")
        background_gray = cv2.resize(background_gray, (w_cap, h_cap), interpolation=cv2.INTER_AREA)
else:
    print("エラー: カメラからの最初のフレーム読み込みに失敗しました。")
    cap.release()
    exit()
# この後のループでは frame_temp は不要なので破棄。

# 3. 検出ループ
while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラからフレームを読み込めませんでした。")
        break

    # 現在のフレームを処理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # 1. 背景差分 (現在のフレーム - 背景フレーム)
    frame_delta = cv2.absdiff(background_gray, gray)

    # 2. 閾値処理 (変化があった部分を白にする)
    # (threshの値は照明に応じて調整)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    
    # 穴埋めとノイズ除去
    thresh = cv2.dilate(thresh, None, iterations=2) 
    
    # 3. 輪郭検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 4. 面積のしきい値でフィルタリング
        if area > 1500: # 変化した領域が一定以上であれば検出とする
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Plastic Bag Detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            detected = True
            break
            
    if not detected:
        cv2.putText(frame, "No Plastic Bag", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Detection", frame)
    cv2.imshow("Threshold", thresh) # 検出に使われている変化の画像

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()