# Smart Traffic Monitoring System

AI-powered traffic monitoring using Python, YOLO, OpenCV, FastAPI and SQLite.

## Features
- YOLO vehicle detection and ByteTrack tracking
- Car, motorcycle, bus and truck counting
- Traffic density and congestion analysis
- Webcam, MP4 and RTSP input
- Live annotated browser dashboard
- FastAPI REST API
- SQLite traffic history
- Traffic alerts
- CSV export
- Automatic YOLO model download on first run

## Windows setup

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python run.py
```

If `py` is unavailable, use `python -m venv .venv`.

Open:
http://127.0.0.1:8000

API docs:
http://127.0.0.1:8000/docs

## Video source

For webcam:
VIDEO_SOURCE=0

For a video:
VIDEO_SOURCE=videos/traffic.mp4

For an RTSP camera:
VIDEO_SOURCE=rtsp://username:password@camera-ip:554/stream

The default YOLO model is `yolo11n.pt`; Ultralytics downloads it automatically.

## API
GET /api/status
GET /api/traffic/current
GET /api/traffic/history
GET /api/vehicles
GET /api/alerts
GET /api/export/csv
POST /api/detection/start
POST /api/detection/stop
GET /video_feed

## Notes

Density thresholds are demo thresholds and should be calibrated for a real road/camera.
Speed estimation and accident detection are intentionally not enabled in this base release because reliable real-world results require camera calibration and additional training data.
