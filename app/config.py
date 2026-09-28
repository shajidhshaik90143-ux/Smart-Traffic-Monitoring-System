import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

raw_source = os.getenv("VIDEO_SOURCE", "0")
VIDEO_SOURCE = int(raw_source) if raw_source.isdigit() else raw_source
MODEL_NAME = os.getenv("MODEL_NAME", "yolo11n.pt")
CONFIDENCE = float(os.getenv("CONFIDENCE", "0.35"))
SAVE_OUTPUT = env_bool("SAVE_OUTPUT")
FRAME_SKIP = max(1, int(os.getenv("FRAME_SKIP", "1")))
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/traffic.db")
STATIC_DIR = BASE_DIR / "static"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
