import cv2
import threading
import time
from collections import Counter
from pathlib import Path
from ultralytics import YOLO

from .config import MODEL_NAME, CONFIDENCE, VIDEO_SOURCE, FRAME_SKIP, SAVE_OUTPUT, VEHICLE_CLASSES
from .traffic_engine import TrafficEngine

class TrafficDetector:
    def __init__(self, db):
        self.db = db
        self.engine = TrafficEngine()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.latest_jpeg = None
        self.frame_number = 0
        self.model = None
        self.error = None

    def load_model(self):
        if self.model is None:
            self.model = YOLO(MODEL_NAME)

    def start(self):
        if self.running:
            return
        self.running = True
        self.error = None
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def status(self):
        return {"running": self.running, "error": self.error, "has_frame": self.latest_jpeg is not None}

    def get_stats(self):
        return dict(self.engine.stats)

    def get_frame(self):
        with self.lock:
            return self.latest_jpeg

    def _worker(self):
        cap = None
        writer = None
        try:
            self.load_model()
            cap = cv2.VideoCapture(VIDEO_SOURCE)
            if not cap.isOpened():
                raise RuntimeError(
                    f"Could not open VIDEO_SOURCE={VIDEO_SOURCE}. "
                    "For webcam use 0; for video use videos/traffic.mp4."
                )

            while self.running:
                ok, frame = cap.read()

                if not ok:
                    if isinstance(VIDEO_SOURCE, str):
                        cap.release()
                        cap = cv2.VideoCapture(VIDEO_SOURCE)
                        if not cap.isOpened():
                            raise RuntimeError("Video source ended or could not be reopened.")
                        continue
                    time.sleep(0.2)
                    continue

                self.frame_number += 1
                if self.frame_number % FRAME_SKIP != 0:
                    continue

                results = self.model.track(
                    frame, persist=True, conf=CONFIDENCE,
                    verbose=False, tracker="bytetrack.yaml"
                )
                result = results[0]
                counts = Counter()
                annotated = frame.copy()

                if result.boxes is not None:
                    for box in result.boxes:
                        cls_id = int(box.cls[0].item())
                        if cls_id not in VEHICLE_CLASSES:
                            continue
                        label = VEHICLE_CLASSES[cls_id]
                        counts[label] += 1

                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        track_id = int(box.id[0].item()) if box.id is not None else None
                        text = label + (f" #{track_id}" if track_id is not None else "")

                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 220, 255), 2)
                        cv2.putText(
                            annotated, text, (x1, max(20, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2
                        )

                stats = self.engine.update(counts)

                if self.frame_number % 30 == 0:
                    self.db.insert_traffic(stats)
                    alert = self.engine.alert()
                    if alert:
                        self.db.insert_alert(*alert)

                overlay = (
                    f"Traffic: {stats['density']} | Vehicles: {stats['total']} | "
                    f"Cars: {stats['cars']} | Bikes: {stats['motorcycles']} | "
                    f"Buses: {stats['buses']} | Trucks: {stats['trucks']}"
                )
                cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 38), (20, 20, 20), -1)
                cv2.putText(
                    annotated, overlay, (10, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
                )

                if SAVE_OUTPUT and writer is None:
                    out_path = Path("data") / "traffic_output.mp4"
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    fps = cap.get(cv2.CAP_PROP_FPS) or 20
                    writer = cv2.VideoWriter(
                        str(out_path), fourcc, fps,
                        (annotated.shape[1], annotated.shape[0])
                    )
                if SAVE_OUTPUT and writer is not None:
                    writer.write(annotated)

                ok, encoded = cv2.imencode(
                    ".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80]
                )
                if ok:
                    with self.lock:
                        self.latest_jpeg = encoded.tobytes()

        except Exception as exc:
            self.error = str(exc)
        finally:
            self.running = False
            if cap is not None:
                cap.release()
            if writer is not None:
                writer.release()
