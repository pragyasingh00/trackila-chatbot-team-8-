import re

# ------------------------
# Language detection
# ------------------------
def detect_language(text: str) -> str:
    """
    Detect whether user input is in Hindi/Hinglish or English.
    """
    hindi_keywords = [
        "namaste", "bus", "kiraya", "baje", "driver",
        "shikayat", "deri", "nahi", "kidar", "kaise",
        "ganda", "rude", "late", "nahi mila", "complaint"
    ]
    for word in hindi_keywords:
        if word in text.lower():
            return "hi"
    return "en"


# ------------------------
# Intent classification
# ------------------------
def get_intent(user_input: str) -> dict:
    """
    Very simple rule-based intent classifier for the chatbot.
    Returns dict with intent + extracted entities + detected language.
    """
    text = user_input.lower()
    lang = detect_language(text)

    # Extract bus number if present
    bus_number_match = re.search(r"\b\d{2,4}\b", text)
    bus_number = bus_number_match.group() if bus_number_match else None

    # ----- Greeting -----
    if any(word in text for word in ["hello", "hi", "hey", "namaste"]):
        return {"intent": "greetings", "lang": lang}

    # ----- Fare info -----
    if "fare" in text or "kiraya" in text or "price" in text:
        return {"intent": "fare_info", "bus_number": bus_number, "lang": lang}

    # ----- Timing info -----
    if "time" in text or "timing" in text or "baje" in text:
        return {"intent": "timing_info", "bus_number": bus_number, "lang": lang}

    # ----- Tracking -----
    if "track" in text or "location" in text or "kidhar" in text or "kahaan" in text:
        return {"intent": "track_bus", "bus_number": bus_number, "lang": lang}

    # ----- Status (delay / on-time) -----
    if "late" in text or "delay" in text or "deri" in text or "status" in text:
        return {"intent": "status_info", "bus_number": bus_number, "lang": lang}

    # ----- Complaint -----
    if any(word in text for word in [
        "complaint", "shikayat", "issue", "problem",
        "driver", "rude", "ganda", "bad", "late", "not found", "nahi mila"
    ]):
        return {
            "intent": "lodge_complaint",
            "bus_number": bus_number,
            "complaint_text": user_input,
            "lang": lang,
        }

    # ----- Route / Next Bus -----
    if "from" in text or "to" in text or "se" in text or "ke liye" in text or "buses" in text:
        # Extract source and destination
        src, dst = None, None
        period, ask_next = None, False

        # English-style "from X to Y"
        match = re.search(r"from\s+(\w+)\s+to\s+(\w+)", text)
        if match:
            src, dst = match.group(1).capitalize(), match.group(2).capitalize()

        # Hindi-style "X se Y"
        match = re.search(r"(\w+)\s+se\s+(\w+)", text)
        if match:
            src, dst = match.group(1).capitalize(), match.group(2).capitalize()

        # Period keywords
        if "morning" in text or "subah" in text:
            period = "morning"
        elif "afternoon" in text or "dopahar" in text:
            period = "afternoon"
        elif "evening" in text or "shaam" in text:
            period = "evening"
        elif "night" in text or "raat" in text:
            period = "night"

        # Ask for next bus
        if "next" in text or "agla" in text:
            ask_next = True

        return {
            "intent": "route_info",
            "source": src,
            "destination": dst,
            "period": period,
            "ask_next": ask_next,
            "lang": lang,
        }

    # ----- Default fallback -----
    return {"intent": "unknown", "lang": lang}
