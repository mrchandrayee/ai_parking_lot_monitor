from dataclasses import dataclass
from .geometry import intersection_over_union

@dataclass
class Track:
    track_id: int
    box: tuple
    class_id: int
    age: int = 0

class IoUTracker:
    """Small dependency-free tracker; suitable for fixed-camera parking footage."""
    def __init__(self, max_age=18, match_iou=0.20):
        self.max_age = int(max_age)
        self.match_iou = float(match_iou)
        self.tracks = {}
        self.next_id = 1

    def update(self, detections):
        for track in self.tracks.values():
            track.age += 1
        unmatched = set(self.tracks.keys())
        for det in detections:
            best_id, best_score = None, 0.0
            for tid in list(unmatched):
                tr = self.tracks[tid]
                if tr.class_id != det.class_id:
                    continue
                score = intersection_over_union(det.box, tr.box)
                if score > best_score:
                    best_id, best_score = tid, score
            if best_id is not None and best_score >= self.match_iou:
                tr = self.tracks[best_id]
                tr.box, tr.age = det.box, 0
                det.track_id = best_id
                unmatched.discard(best_id)
            else:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = Track(tid, det.box, det.class_id, 0)
                det.track_id = tid
        self.tracks = {tid: tr for tid, tr in self.tracks.items() if tr.age <= self.max_age}
        return detections
