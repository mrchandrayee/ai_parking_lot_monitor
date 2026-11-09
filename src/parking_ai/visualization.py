import cv2

FREE = (60, 190, 70)
OCCUPIED = (45, 45, 225)
WHITE = (245, 245, 245)

def draw_text(frame, text, xy, scale=0.55, color=WHITE, thickness=1):
    cv2.putText(frame, str(text), tuple(map(int, xy)), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thickness, cv2.LINE_AA)

def draw_overlay(frame, detections, slots, summary):
    out = frame.copy()
    for slot in slots:
        color = OCCUPIED if slot.occupied else FREE
        cv2.polylines(out, [slot.polygon], True, color, 2, cv2.LINE_AA)
        x, y = slot.polygon[0]
        label = f"{slot.slot_id}: {'OCCUPIED' if slot.occupied else 'FREE'}"
        draw_text(out, label, (x+3, y+18), 0.42, color, 1)
    for det in detections:
        x1,y1,x2,y2 = map(int, det.box)
        cv2.rectangle(out, (x1,y1), (x2,y2), (255, 120, 40), 2)
        tag = f"{det.label} #{det.track_id} {det.confidence:.2f}"
        draw_text(out, tag, (x1, max(16,y1-6)), 0.42, (255, 220, 100), 1)
    panel = f"PARKING LOT  |  TOTAL {summary['total']}  FREE {summary['free']}  OCCUPIED {summary['occupied']}"
    cv2.rectangle(out, (8,8), (min(out.shape[1]-8, 620), 42), (20,20,20), -1)
    draw_text(out, panel, (16,31), 0.52, WHITE, 1)
    return out
