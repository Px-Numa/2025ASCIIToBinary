import cv2
from ultralytics import YOLO

#モデル選択n<s<m<l<x(軽量～高精度)
model = YOLO("yolov8n.pt")

# webカメラでリアルタイム検出
# (source= 0はWebカメラ, show=ウィンドウに表示, classes=[0] 0で人検出のみ, conf=人間だと判断する閾値)
result = model.predict(source=0, show=True, classes=[0], conf=0.3)

cv2.waitKey(1) & 0xFF == ord("q")

