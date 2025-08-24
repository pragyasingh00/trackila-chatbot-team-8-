import csv
import os
from datetime import datetime

# --------- Bus lookups ---------

def search_buses_by_number(buses, bus_number: str):
    for b in buses:
        if str(b.get("bus_id")) == str(bus_number):
            return b
    return None

def _parse_time(tstr: str):
    """
    Parse times like '8:30 AM' -> datetime.time
    """
    # try multiple formats
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            return datetime.strptime(tstr.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized time format: {tstr}")

def buses_between(buses, source: str, destination: str):
    s = (source or "").lower()
    d = (destination or "").lower()
    found = [b for b in buses if b.get("source","").lower() == s and b.get("destination","").lower() == d]
    # sort by time ascending
    try:
        found.sort(key=lambda x: _parse_time(x["time"]))
    except Exception:
        pass
    return found

def next_bus_between(buses, source: str, destination: str):
    """
    Picks the next upcoming bus based on current local time.
    If all buses have already departed today, returns the earliest bus.
    """
    from datetime import datetime as _dt
    now = _dt.now().time()
    matches = buses_between(buses, source, destination)
    if not matches:
        return None
    after = [b for b in matches if _parse_time(b["time"]) >= now]
    return after[0] if after else matches[0]

def last_bus_in_period_between(buses, source: str, destination: str, period: str):
    """
    period: morning(05:00-11:59) | afternoon(12:00-16:59) | evening(17:00-20:59) | night(21:00-23:59)
    Returns the latest bus in that window; None if none found.
    """
    bounds = {
        "morning":  ("05:00", "11:59"),
        "afternoon":("12:00", "16:59"),
        "evening":  ("17:00", "20:59"),
        "night":    ("21:00", "23:59"),
    }
    if period not in bounds:
        return None
    start, end = bounds[period]
    t_start = _parse_time(start)
    t_end = _parse_time(end)

    matches = buses_between(buses, source, destination)
    in_window = [b for b in matches if t_start <= _parse_time(b["time"]) <= t_end]
    if not in_window:
        return None
    # latest in window
    in_window.sort(key=lambda x: _parse_time(x["time"]))
    return in_window[-1]

# --------- Complaint logging (CSV) ---------

def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def _make_ticket_id():
    # C-YYYYMMDDHHMMSS-XYZ
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    # deterministic small suffix from time seconds to keep simple
    suffix = str(int(datetime.now().strftime("%S")) * 7 % 997).zfill(3)
    return f"C-{ts}-{suffix}"

def save_complaint_csv(bus_number: str, complaint_text: str, csv_path: str = "data/complaints.csv") -> str:
    _ensure_dir(csv_path)
    ticket_id = _make_ticket_id()
    now = datetime.now().isoformat(timespec="seconds")
    header = ["ticket_id", "bus_number", "complaint", "datetime"]

    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow([ticket_id, bus_number, complaint_text, now])
    return ticket_id

# --------- Delay / status simulation ---------

def get_bus_delay_minutes(bus_id: str) -> int:
    """
    Deterministic pseudo-delay based on bus_id digits.
    0 => on time; otherwise 5-24 minutes late.
    """
    try:
        n = sum(int(c) for c in str(bus_id) if c.isdigit())
    except Exception:
        n = 7
    delay = (n * 7) % 25  # 0..24
    return delay  # 0 means on time
