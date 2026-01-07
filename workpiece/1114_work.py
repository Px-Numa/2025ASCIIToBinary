"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
<ワーク検出>
更新日：2025.11.14
作成者：橋本

# References

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import cv2
import numpy as np
import os

# --- 設定 ---
# ワーク有無判定のマスク画像ファイルパス
# 実際の環境に合わせて、パスを修正してください。
MASK_OSHIDASHI_FILEPATH = 'image/mask_work_detection.png' 
# ワークありと判断する白色領域のしきい値 (%) (元のコード: 24.45)
THRESHOLD_RATIO = 20.80 
# 処理を行う画像サイズ (元のコード: 640x480)
RESIZE_WIDTH = 640
RESIZE_HEIGHT = 480
# 2値化処理のしきい値 (元のコード: 89)
BINARIZATION_THRESHOLD = 89
# ----------------

# 1. マスク画像の読み込み
try:
    # グレースケールで読み込み
    mask = cv2.imread(MASK_OSHIDASHI_FILEPATH, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"マスク画像ファイルが見つかりません: {MASK_OSHIDASHI_FILEPATH}")
except Exception as e:
    print(e)
    # エラーが発生したらプログラムを終了
    exit()

# Webカメラを開く (0 は通常、プライマリカメラ)
cap = cv2.VideoCapture(0) 

# カメラが開けたか確認
if not cap.isOpened():
    print("Webカメラを開けませんでした。カメラが接続されているか、他のアプリケーションで使用されていないか確認してください。")
    exit()

# ループの外で前回結果を保持する変数を初期化  
# 比較用: 前回の「状態」（例: "OK" or "NG"）を保持
last_result_state = "" 

# --- メインのリアルタイム処理ループ ---
while True:
    # 2. フレームの読み込み (リアルタイム映像)
    ret, frame = cap.read()
    if not ret:
        print("フレームの読み込みに失敗しました。")
        break

    # 3. 画像処理の準備とリサイズ
    
    cam_size = (RESIZE_WIDTH, RESIZE_HEIGHT)
    
    # カメラ画像をリサイズ
    image = cv2.resize(frame, cam_size)
    # マスク画像をリサイズ
    mask_resized = cv2.resize(mask, cam_size)

    # 画像全体の面積を算出 (ピクセル数)
    image_size = cam_size[0] * cam_size[1] 

    # 4. 画像処理の実行（ロジック）
    
    # カメラ画像をグレースケールに変換
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # マスク処理 (マスク画像が白い部分だけを抽出)
    masked_image = cv2.bitwise_and(gray_image, mask_resized)

    # 2値化処理 (しきい値89)
    thresh_value, image_area = cv2.threshold(masked_image, BINARIZATION_THRESHOLD, 255, cv2.THRESH_BINARY)

    # 白色のピクセル数 (ワークと判断される領域) を算出
    whitePixels = cv2.countNonZero(image_area) 
    
    # 黒色の部分を算出 (元のコードにあったが、判定には使用しない)
    # blackPixels = image_size - whitePixels 

    # 白色の領域の割合を算出
    whiteAreaRatio = (whitePixels / image_size) * 100 
    
    # 5. 検知結果の判定と表示
    result_text = ""
    result_color = (0, 0, 255) # デフォルトは赤
    current_state = "" # 今回の単純な状態（比較用）

    if whiteAreaRatio >= THRESHOLD_RATIO:
        result_text = f"ワークセットOK (Ratio: {whiteAreaRatio:.2f} %)" # 表示用（詳細）
        result_color = (0, 255, 0) # 緑
        current_state = "OK"
    else:
        result_text = f"ワークセットNG (Ratio: {whiteAreaRatio:.2f} %)" # 表示用（詳細）
        result_color = (255, 0, 0) # 青
        current_state = "NG"

    # 以前の「状態」と異なる場合のみ、コンソールに出力
    if current_state != last_result_state:
        print(result_text) # 状態が変わったときのみ、詳細なテキストを出力
        last_result_state = current_state # 新しい状態を保存
        
    # 元画像に結果テキストを表示 (画像表示には詳細な result_text を使う)
    cv2.putText(image, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, result_color, 2, cv2.LINE_AA)
    
    # 処理された領域（2値化後のマスク画像）を表示
    cv2.imshow('Masked and Binarized Area', image_area)
    
    # 元画像に結果を重ねて表示
    cv2.imshow('Real-time Work Detection', image)

    # 'q'キーが押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 終了処理
cap.release()
cv2.destroyAllWindows()