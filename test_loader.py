from data_loader import DataLoader
from utils import (
    search_buses_by_number,
    buses_between,
    next_bus_between,
    last_bus_in_period_between,
    save_complaint_csv,
    get_bus_delay_minutes,
)

loader = DataLoader("data/sample_buses.json")
buses = loader.load_json()

print(f"Loaded {len(buses)} buses")

# Find by number
b = search_buses_by_number(buses, "202")
print("Find 202:", b)

# Route list
route = buses_between(buses, "Delhi", "Karnal")
print("Delhi -> Karnal:", route)

# Next bus
nb = next_bus_between(buses, "Delhi", "Karnal")
print("Next Delhi->Karnal:", nb)

# Last bus at night
lb_night = last_bus_in_period_between(buses, "Delhi", "Karnal", "night")
print("Last at night Delhi->Karnal:", lb_night)

# Complaint log
tid = save_complaint_csv("702", "Driver was rude")
print("Complaint Ticket:", tid)

# Delay check
print("Delay for 101:", get_bus_delay_minutes("101"))
