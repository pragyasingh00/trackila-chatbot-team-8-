import json
import random

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_json(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def simulate_bus_locations(self, buses):
        """
        Simulate live bus locations using a fixed pool of city names.
        Returns: {bus_id: {"location": str}}
        """
        locations = [
            "Panipat", "Karnal", "Kurukshetra", "Ambala",
            "Delhi", "Sonipat", "Rohini", "Dwarka", "Rajouri Garden"
        ]
        out = {}
        for bus in buses:
            bus_id = str(bus["bus_id"])
            out[bus_id] = {"location": random.choice(locations)}
        return out
