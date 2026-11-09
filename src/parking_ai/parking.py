from dataclasses import dataclass
from .geometry import normalized_polygon, box_anchor, point_in_polygon, box_polygon_overlap

@dataclass
class ParkingSlot:
    slot_id: str
    polygon: object
    occupied: bool = False
    vehicle_id: int = -1
    overlap: float = 0.0

class ParkingLot:
    def __init__(self, slot_configs, width, height, threshold=0.18, anchor="bottom_center"):
        self.threshold = float(threshold)
        self.anchor = anchor
        self.slots = [
            ParkingSlot(str(item["id"]), normalized_polygon(item["polygon"], width, height))
            for item in slot_configs
        ]

    def update(self, detections):
        for slot in self.slots:
            slot.occupied, slot.vehicle_id, slot.overlap = False, -1, 0.0
            best = None
            for det in detections:
                overlap = box_polygon_overlap(det.box, slot.polygon)
                anchor_inside = point_in_polygon(box_anchor(det.box, self.anchor), slot.polygon)
                score = max(overlap, 0.35 if anchor_inside else 0.0)
                if score > slot.overlap:
                    slot.overlap = score
                    best = det
            if best is not None and slot.overlap >= self.threshold:
                slot.occupied = True
                slot.vehicle_id = best.track_id
        return self.slots

    def summary(self):
        occupied = sum(s.occupied for s in self.slots)
        return {"total": len(self.slots), "occupied": occupied, "free": len(self.slots)-occupied}
