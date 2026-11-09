# AI Parking Lot Monitor

A real-time parking occupancy detection system powered by [YOLOv11](https://docs.ultralytics.com/) and OpenCV. It detects vehicles in video frames, tracks them across time, and evaluates configurable parking-space polygons — displaying a live FREE / OCCUPIED overlay on every slot.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![YOLOv11](https://img.shields.io/badge/YOLOv11-ultralytics-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9%2B-green?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Demo

> Point the system at a parking-lot video and it will annotate every bay in real time.

```
Total: 6  |  Free: 2  |  Occupied: 4
```

Annotated output is saved to `runs/parking_output.mp4`.

---

## Features

| Feature | Detail |
|---|---|
| Vehicle detection | YOLOv11n (car, motorcycle, bus, truck — COCO classes 2, 3, 5, 7) |
| Object tracking | Lightweight IoU-based tracker with configurable max-age |
| Occupancy logic | Per-slot polygon overlap + bottom-center anchor heuristic |
| Live HUD | Total / Free / Occupied count overlaid on each frame |
| Input flexibility | Video file **or** webcam (`--source 0`) |
| Annotated output | Writes MP4 to `runs/parking_output.mp4` by default |
| Config-driven | All detector, tracker, and slot parameters live in one YAML file |

---

## Project Structure

```
ai_parking_lot_monitor/
├── configs/
│   └── parking.yaml          # All tuneable parameters + slot polygons
├── src/parking_ai/
│   ├── __init__.py
│   ├── cli.py                # Entry point (argparse)
│   ├── config.py             # YAML loader + source resolver
│   ├── detection.py          # VehicleDetector wrapping Ultralytics YOLO
│   ├── geometry.py           # Polygon math, IoU, anchor helpers
│   ├── tracking.py           # IoUTracker — stable IDs across frames
│   ├── parking.py            # ParkingLot + per-slot occupancy state
│   ├── pipeline.py           # ParkingLotPipeline — wires all modules together
│   └── visualization.py     # HUD drawing helpers
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & set up the environment

```bash
git clone https://github.com/<your-username>/ai_parking_lot_monitor.git
cd ai_parking_lot_monitor

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> Ultralytics downloads **`yolo11n.pt`** automatically on first run (internet required). You can swap the model in `configs/parking.yaml`.

### 2. Configure your parking slots

Open `configs/parking.yaml` and replace the sample polygons with the actual bay corners from your camera feed. Coordinates are **normalized (0.0 – 1.0)** relative to the frame:

```yaml
parking:
  slots:
    - id: "A01"
      polygon: [[0.10, 0.25], [0.22, 0.25], [0.22, 0.48], [0.10, 0.48]]
    - id: "A02"
      polygon: [[0.24, 0.25], [0.36, 0.25], [0.36, 0.48], [0.24, 0.48]]
```

### 3. Run

**Video file:**
```bash
PYTHONPATH=src python -m parking_ai.cli --config configs/parking.yaml --source input.mp4
```

**Webcam:**
```bash
PYTHONPATH=src python -m parking_ai.cli --config configs/parking.yaml --source 0
```

**Headless (no display window):**
```bash
PYTHONPATH=src python -m parking_ai.cli --config configs/parking.yaml --source input.mp4 --no-show
```

---

## Configuration Reference

All settings live in `configs/parking.yaml`:

```yaml
video:
  source: "input.mp4"          # path to video file or 0 for webcam
  output: "runs/parking_output.mp4"
  show: true                   # display live window
  resize_width: 960            # resize input frames to this width

detector:
  model: "yolo11n.pt"          # any Ultralytics-compatible model
  confidence: 0.28             # detection confidence threshold
  iou: 0.50                    # NMS IoU threshold
  classes: [2, 3, 5, 7]        # COCO: car, motorcycle, bus, truck

tracking:
  enabled: true
  max_age: 18                  # frames to keep a lost track alive
  match_iou: 0.20              # minimum IoU to associate detection → track

parking:
  occupancy_threshold: 0.18   # overlap fraction to mark a slot occupied
  anchor: "bottom_center"      # bottom_center | center
  slots: [...]                 # list of {id, polygon} entries
```

### Tuning tips

- **`occupancy_threshold`** — raise it if adjacent vehicles trigger neighboring bays; lower it if partially visible cars are missed.
- **`anchor: bottom_center`** — works best for side/elevated cameras where the wheel contact point is visible. Switch to `center` for overhead views.
- **`max_age`** — increase for slower-moving traffic or scenes with occlusion.
- **Model** — swap `yolo11n.pt` → `yolo11s.pt` / `yolo11m.pt` for better accuracy at the cost of speed.

---

## How It Works

```
Video frame
    │
    ▼
VehicleDetector (YOLOv11)  ──► raw bounding boxes
    │
    ▼
IoUTracker  ──► boxes with stable track IDs
    │
    ▼
ParkingLot.update()  ──► per-slot overlap check
    │
    ▼
draw_overlay()  ──► annotated frame written to output
```

1. **Detection** — YOLOv11n runs inference on each (optionally resized) frame and returns bounding boxes for the configured vehicle classes.
2. **Tracking** — An IoU-based tracker associates boxes across frames, assigning stable IDs and suppressing flicker.
3. **Occupancy** — For each parking slot polygon, the system checks whether any tracked vehicle's anchor point (or box overlap) exceeds the configured threshold.
4. **Visualization** — Slot polygons are drawn in green (free) or red (occupied), with a summary HUD in the top-left corner.

---

## Requirements

| Package | Version |
|---|---|
| Python | 3.10 or 3.11 |
| ultralytics | ≥ 8.3.0 |
| opencv-python | ≥ 4.9.0 |
| numpy | ≥ 1.26.0 |
| PyYAML | ≥ 6.0.1 |

Install everything with:
```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** this repository
2. **Create a branch** for your feature or fix: `git checkout -b feature/my-improvement`
3. **Commit** your changes with a clear message
4. **Push** to your fork and open a **Pull Request**

### Ideas for contribution

- [ ] ByteTrack / BoT-SORT integration for crowded scenes
- [ ] Multi-camera support
- [ ] REST API / WebSocket endpoint for live occupancy data
- [ ] Web dashboard (Streamlit / Gradio)
- [ ] Slot polygon calibration tool (click-to-define bays on a frame)
- [ ] Docker image

Please open an issue first if you're planning a large change, so we can discuss the approach.

---

## Known Limitations

- **Slot polygons are camera-specific.** The sample coordinates in `configs/parking.yaml` are illustrative; you must replace them for your scene.
- **IoU tracker is intentionally lightweight.** For dense scenes or long occlusions, plug in ByteTrack/BoT-SORT via Ultralytics.
- **No model weights or sample footage are bundled.** YOLOv11n downloads automatically; provide your own video.
- This is a clean reconstruction from observable behavior — not a byte-for-byte recovery of any original codebase.

---

## License

This project is released under the [MIT License](LICENSE).

---

## Acknowledgements

- [Ultralytics YOLOv11](https://docs.ultralytics.com/) for the detection backbone
- [OpenCV](https://opencv.org/) for video I/O and drawing
