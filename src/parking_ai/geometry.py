import cv2
import numpy as np

def normalized_polygon(points, width, height):
    pts = np.asarray(points, dtype=np.float32)
    pts[:, 0] *= width
    pts[:, 1] *= height
    return np.round(pts).astype(np.int32)

def box_anchor(box, mode="bottom_center"):
    x1, y1, x2, y2 = map(float, box)
    if mode == "center":
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
    return ((x1 + x2) / 2.0, y2)

def box_polygon_overlap(box, polygon):
    # Fraction of the detection box covered by a parking polygon.
    x1, y1, x2, y2 = map(float, box)
    bw, bh = max(1.0, x2-x1), max(1.0, y2-y1)
    mask = np.zeros((max(1, int(y2)+2), max(1, int(x2)+2)), dtype=np.uint8)
    # Use a local crop to avoid allocating a full-frame mask.
    px = np.asarray(polygon, dtype=np.int32).copy()
    ox, oy = max(0, int(x1)), max(0, int(y1))
    ex, ey = max(ox+1, int(x2)+1), max(oy+1, int(y2)+1)
    local = np.zeros((ey-oy, ex-ox), dtype=np.uint8)
    px[:, 0] -= ox
    px[:, 1] -= oy
    cv2.fillPoly(local, [px], 1)
    ix1, iy1 = max(0, int(x1)-ox), max(0, int(y1)-oy)
    ix2, iy2 = min(local.shape[1], int(x2)-ox), min(local.shape[0], int(y2)-oy)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    return float(local[iy1:iy2, ix1:ix2].sum()) / (bw * bh)

def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.asarray(polygon, np.int32), point, False) >= 0

def intersection_over_union(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    x1, y1 = max(ax1,bx1), max(ay1,by1)
    x2, y2 = min(ax2,bx2), min(ay2,by2)
    inter = max(0,x2-x1) * max(0,y2-y1)
    area_a = max(0,ax2-ax1) * max(0,ay2-ay1)
    area_b = max(0,bx2-bx1) * max(0,by2-by1)
    return inter / max(1e-9, area_a + area_b - inter)
