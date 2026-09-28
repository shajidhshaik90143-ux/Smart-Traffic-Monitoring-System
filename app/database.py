import sqlite3
from pathlib import Path
from datetime import datetime

class TrafficDatabase:
    def __init__(self, path: Path):
        self.path = str(path)
        self.init()

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def init(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS traffic_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total INTEGER NOT NULL,
                    cars INTEGER NOT NULL,
                    motorcycles INTEGER NOT NULL,
                    buses INTEGER NOT NULL,
                    trucks INTEGER NOT NULL,
                    density TEXT NOT NULL,
                    congestion INTEGER NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL
                )
            """)

    def insert_traffic(self, stats):
        with self.connect() as con:
            con.execute("""
                INSERT INTO traffic_records
                (timestamp,total,cars,motorcycles,buses,trucks,density,congestion)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                datetime.now().isoformat(timespec="seconds"),
                stats["total"], stats["cars"], stats["motorcycles"],
                stats["buses"], stats["trucks"], stats["density"],
                int(stats["congestion"])
            ))

    def insert_alert(self, alert_type, message, severity):
        with self.connect() as con:
            con.execute("""
                INSERT INTO alerts(timestamp,alert_type,message,severity)
                VALUES (?,?,?,?)
            """, (
                datetime.now().isoformat(timespec="seconds"),
                alert_type, message, severity
            ))

    def history(self, limit=100):
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM traffic_records ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def alerts(self, limit=50):
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
