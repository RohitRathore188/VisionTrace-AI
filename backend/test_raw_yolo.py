import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

# Frame 000300 or 000180
img_path = r'd:\Projects\VisionTrace AI\backend\data\frames\029841e0-53b6-4748-8114-6c7b74ce5c9e\frame_000180.jpg'
img = cv2.imread(img_path)
h, w = img.shape[:2]

results = model(img, conf=0.15)
print(f"Confidence threshold 0.15 results count: {len(results[0].boxes)}")
for box in results[0].boxes:
    conf = float(box.conf[0])
    cls_id = int(box.cls[0])
    raw_label = model.names[cls_id]
    xyxy = box.xyxy[0].tolist()
    
    # Normalized BBox
    xmin = round(xyxy[0] / w, 4)
    ymin = round(xyxy[1] / h, 4)
    xmax = round(xyxy[2] / w, 4)
    ymax = round(xyxy[3] / h, 4)
    print(f"  Class: {raw_label} ({cls_id}) | Conf: {conf:.2f} | BBox px: {[int(x) for x in xyxy]} | BBox norm: [xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}]")
