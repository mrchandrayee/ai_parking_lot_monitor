from dataclasses import dataclass
from ultralytics import YOLO

@dataclass
class Detection:
    box: tuple
    confidence: float
    class_id: int
    label: str
    track_id: int = -1

class VehicleDetector:
    def __init__(self, model, confidence=0.28, iou=0.5, classes=None):
        self.model = YOLO(model)
        self.confidence = float(confidence)
        self.iou = float(iou)
        self.classes = classes

    def detect(self, frame):
        result = self.model.predict(
            source=frame, conf=self.confidence, iou=self.iou,
            classes=self.classes, verbose=False
        )[0]
        detections = []
        names = result.names
        if result.boxes is None:
            return detections
        for item in result.boxes:
            xyxy = item.xyxy[0].cpu().numpy().tolist()
            cls = int(item.cls[0].item())
            conf = float(item.conf[0].item())
            detections.append(Detection(
                box=tuple(map(float, xyxy)), confidence=conf,
                class_id=cls, label=str(names.get(cls, cls))
            ))
        return detections
