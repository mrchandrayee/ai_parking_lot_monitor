import cv2
from .detection import VehicleDetector
from .tracking import IoUTracker
from .parking import ParkingLot
from .visualization import draw_overlay

class ParkingLotPipeline:
    def __init__(self, cfg, frame_width, frame_height):
        dcfg = cfg.get("detector", {})
        self.detector = VehicleDetector(
            dcfg.get("model", "yolo11n.pt"),
            dcfg.get("confidence", 0.28),
            dcfg.get("iou", 0.5),
            dcfg.get("classes", [2,3,5,7])
        )
        tcfg = cfg.get("tracking", {})
        self.tracker = IoUTracker(tcfg.get("max_age",18), tcfg.get("match_iou",0.2)) if tcfg.get("enabled",True) else None
        pcfg = cfg.get("parking", {})
        self.parking = ParkingLot(
            pcfg.get("slots", []), frame_width, frame_height,
            pcfg.get("occupancy_threshold",0.18), pcfg.get("anchor","bottom_center")
        )

    def process(self, frame):
        detections = self.detector.detect(frame)
        if self.tracker:
            detections = self.tracker.update(detections)
        slots = self.parking.update(detections)
        summary = self.parking.summary()
        return draw_overlay(frame, detections, slots, summary), summary
