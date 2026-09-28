from datetime import datetime

class TrafficEngine:
    def __init__(self):
        self.stats = {
            "total": 0, "cars": 0, "motorcycles": 0,
            "buses": 0, "trucks": 0, "density": "LOW",
            "congestion": False, "timestamp": ""
        }

    def density_for(self, total):
        if total >= 80:
            return "SEVERE"
        if total >= 50:
            return "HIGH"
        if total >= 20:
            return "MEDIUM"
        return "LOW"

    def update(self, counts):
        total = sum(counts.values())
        density = self.density_for(total)
        self.stats = {
            "total": total,
            "cars": counts.get("car", 0),
            "motorcycles": counts.get("motorcycle", 0),
            "buses": counts.get("bus", 0),
            "trucks": counts.get("truck", 0),
            "density": density,
            "congestion": density in {"HIGH", "SEVERE"},
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }
        return self.stats

    def alert(self):
        if self.stats["density"] == "SEVERE":
            return ("HIGH_DENSITY", f"Severe traffic detected: {self.stats['total']} vehicles.", "HIGH")
        if self.stats["density"] == "HIGH":
            return ("HIGH_DENSITY", f"High traffic detected: {self.stats['total']} vehicles.", "MEDIUM")
        return None
