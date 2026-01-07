import cv2
import datetime
import os

# 保存先のディレクトリを作成（既に存在する場合は何もしない）
output_dir = 'image'
os.makedirs(output_dir, exist_ok=True)

# カメラのビデオキャプチャを開始
cap = cv2.VideoCapture(0)

while True:
    # フレームをキャプチャ
    ret, frame = cap.read()
    if not ret:
        break

    # フレームを表示
    cv2.imshow('Live', frame)

    # キー入力を待つ
    key = cv2.waitKey(1) & 0xFF

    # 's'キーが押されたらフレームをキャプチャして保存
    if key == ord('s'):
        # 現在の日時を取得して、ファイル名に含める形式の文字列に変換
        # 例: 20251022_143000
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
        
        # ファイル名を生成
        filename = f"{output_dir}/image_{timestamp}.png"
        
        # 画像を保存
        cv2.imwrite(filename, frame)
        print(f"'{filename}' に画像を保存しました。")

    # 'q'キーが押されたらループから抜ける
    elif key == ord('q'):
        break

# キャプチャをリリースし、ウィンドウを閉じる
cap.release()
cv2.destroyAllWindows()
