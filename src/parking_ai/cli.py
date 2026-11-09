import argparse
from pathlib import Path
import cv2
from .config import load_config, resolve_source
from .pipeline import ParkingLotPipeline

def main():
    parser = argparse.ArgumentParser(description="AI parking-lot vehicle detection and occupancy monitor")
    parser.add_argument("--config", default="configs/parking.yaml")
    parser.add_argument("--source", default=None, help="Video path, image path, folder, or webcam index")
    parser.add_argument("--output", default=None)
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    source = resolve_source(args.source if args.source is not None else cfg["video"].get("source","0"))
    output = args.output or cfg["video"].get("output","runs/parking_output.mp4")
    show = bool(cfg["video"].get("show",True)) and not args.no_show
    resize_width = int(cfg["video"].get("resize_width",960))

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open input source: {source}")

    ok, first = cap.read()
    if not ok:
        raise SystemExit("Input opened but no frames could be read.")
    original_h, original_w = first.shape[:2]
    scale = min(1.0, resize_width / original_w) if resize_width > 0 else 1.0
    width, height = int(original_w*scale), int(original_h*scale)
    first = cv2.resize(first, (width,height)) if scale != 1 else first

    # Slot polygons are interpreted against the processed frame dimensions.
    pipeline = ParkingLotPipeline(cfg, width, height)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps < 1 or fps > 120: fps = 25.0
    writer = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width,height))

    frame = first
    frame_count = 0
    try:
        while True:
            rendered, stats = pipeline.process(frame)
            writer.write(rendered)
            frame_count += 1
            if show:
                cv2.imshow("AI Parking Lot Monitor (q to quit)", rendered)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            ok, raw = cap.read()
            if not ok: break
            frame = cv2.resize(raw, (width,height)) if scale != 1 else raw
    finally:
        cap.release()
        writer.release()
        if show: cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames. Output: {output}")
    print(f"Last frame summary: {stats}")

if __name__ == "__main__":
    main()
