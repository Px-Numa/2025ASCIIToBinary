import cv2

# カメラを開く
cap = cv2.VideoCapture(0)

# いったん解放して再オープン → これでデフォルト値に戻ることが多い
cap.release()
cap = cv2.VideoCapture(0)


# cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

# # キャプチャがオープンしている間続ける
# while(cap.isOpened()):
#     # フレームを読み込む
#     ret, frame = cap.read()
#     if ret == True:
#         # フレームを表示
#         cv2.imshow('Webcam Live', frame)

#         # 'q'キーが押されたらループから抜ける
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     else:
#         break

# # キャプチャをリリースし、ウィンドウを閉じる
# cap.release()
# cv2.destroyAllWindows()