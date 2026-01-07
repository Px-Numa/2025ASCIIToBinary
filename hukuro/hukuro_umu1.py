import cv2
import numpy as np
import os

# --- 設定 ---
# マスク画像のファイルパス（スクリプトと同じフォルダのimageフォルダに置く）
# ファイル名は、ご自身の環境に合わせて修正してください。
MASK_FUKURO_FILEPATH = 'image/hukuro_mask.png'
THRESHOLD_RATIO = 5.0 # 袋ありと判断する白色領域のしきい値 (%)
# ----------------

# 1. マスク画像の読み込み
try:
    # グレースケールで読み込み
    mask = cv2.imread(MASK_FUKURO_FILEPATH, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"マスク画像ファイルが見つかりません: {MASK_FUKURO_FILEPATH}")
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
last_result_text = ""

# --- メインのリアルタイム処理ループ ---
while True:
    # 2. フレームの読み込み (リアルタイム映像)
    ret, frame = cap.read()
    if not ret:
        print("フレームの読み込みに失敗しました。")
        break

    # 3. 画像処理の準備とリサイズ
    
    # カメラ画像のサイズを取得 (width, height)
    cam_size = (frame.shape[1], frame.shape[0])
    
    # ここではカメラ画像の元のサイズに合わせて処理を実行
    image = frame
    mask_resized = cv2.resize(mask, cam_size)

    # 画像全体の面積を算出 (ピクセル数)
    image_size = cam_size[0] * cam_size[1] 

    # 4. 画像処理の実行（ご提示のロジック）
    
    # カメラ画像をグレースケールに変換
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # マスク処理 (マスク画像が白い部分だけを抽出)
    masked_image = cv2.bitwise_and(gray_image, mask_resized)

    # 2値化処理 (しきい値200) -> 袋が明るい/白い場合を想定
    thresh_value, image_area = cv2.threshold(masked_image, 200, 255, cv2.THRESH_BINARY)

    # 白色のピクセル数 (袋と判断される領域) を算出
    whitePixels = cv2.countNonZero(image_area) 

    # 白色の領域の割合を算出
    whiteAreaRatio = (whitePixels / image_size) * 100 
    
    # 5. 検知結果の判定と表示
    result_text = ""
    result_color = (0, 0, 255) # デフォルトは赤

    if whiteAreaRatio >= THRESHOLD_RATIO:
        result_text = f"袋あり (Ratio: {whiteAreaRatio:.2f} %)"
        result_color = (0, 255, 0) # 緑
        # print("袋あり")
    else:
        result_text = f"袋なし (Ratio: {whiteAreaRatio:.2f} %)"
        result_color = (255, 0, 0) # 青
        # print("袋なし")

    # 以前の結果と異なる場合のみ出力
    if result_text != last_result_text:
        print(result_text)
        last_result_text = result_text # 新しい結果を保存
        
    # 元画像に結果テキストを表示
    cv2.putText(image, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, result_color, 2, cv2.LINE_AA)
    
    # 処理された領域（2値化後のマスク画像）を表示
    cv2.imshow('Masked and Binarized Area', image_area)
    
    # 元画像に結果を重ねて表示
    cv2.imshow('Real-time Fukuro Detection', image)

    # 'q'キーが押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 終了処理
cap.release()
cv2.destroyAllWindows()
