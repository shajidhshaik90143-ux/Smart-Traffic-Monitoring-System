import csv
import io
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR, DATABASE_PATH
from .database import TrafficDatabase
from .detector import TrafficDetector

app = FastAPI(
    title="Smart Traffic Monitoring System",
    version="1.0.0",
    description="AI-powered traffic monitoring API"
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

db = TrafficDatabase(DATABASE_PATH)
detector = TrafficDetector(db)

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/status")
def status():
    return detector.status()

@app.get("/api/traffic/current")
def current_traffic():
    return detector.get_stats()

@app.get("/api/traffic/history")
def traffic_history(limit: int = 100):
    return db.history(max(1, min(limit, 1000)))

@app.get("/api/vehicles")
def vehicles():
    s = detector.get_stats()
    return {k: s[k] for k in ("cars", "motorcycles", "buses", "trucks", "total")}

@app.get("/api/alerts")
def alerts(limit: int = 50):
    return db.alerts(max(1, min(limit, 500)))

@app.get("/api/export/csv")
def export_csv():
    rows = db.history(1000)
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("No traffic records yet\n")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_history.csv"}
    )

@app.post("/api/detection/start")
def start_detection():
    detector.start()
    return {"success": True, "message": "Detection started"}

@app.post("/api/detection/stop")
def stop_detection():
    detector.stop()
    return {"success": True, "message": "Detection stopping"}

@app.get("/video_feed")
def video_feed():
    frame = detector.get_frame()
    if frame is None:
        return JSONResponse({"error": "No processed frame yet."}, status_code=404)
    return StreamingResponse(iter([frame]), media_type="image/jpeg")

@app.on_event("startup")
def startup():
    detector.start()

@app.on_event("shutdown")
def shutdown():
    detector.stop()
