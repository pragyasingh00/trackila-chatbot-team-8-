from intent import get_intent
from utils import (
    search_buses_by_number,
    buses_between,
    next_bus_between,
    last_bus_in_period_between,
    save_complaint_csv,
    get_bus_delay_minutes,
)
from data_loader import DataLoader
import re

# Load bus data
loader = DataLoader("data/sample_buses.json")
BUSES = loader.load_json()

print(" Trackila Chatbot started! Type 'exit' to quit.")

# -------- Helper: bilingual response --------
def respond(message_en, message_hi, lang="en"):
    return message_hi if lang == "hi" else message_en


while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ("exit", "quit", "bye"):
        print("Bot: Goodbye! Have a safe journey  / अलविदा! शुभ यात्रा ")
        break

    # detect intent
    intent_data = get_intent(user_input)
    intent = intent_data.get("intent")
    lang = intent_data.get("lang", "en")  # default English if missing

    # DEBUGGING LINE (optional, remove later)
    # print("DEBUG INTENT:", intent_data)

    # -------- Greetings ----------
    if intent == "greetings":
        print("Bot:", respond(
            "Hello! How can I assist you today?",
            "Namaste! Main aapki kaise madad kar sakta hoon?",
            lang
        ))
        continue

    # -------- Fare ----------
    if intent == "fare_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            print("Bot:", respond(
                "Please provide a bus number to check the fare.",
                "Kirpya bus number bataye taaki main kiraya bata sakun.",
                lang
            ))
            continue
        bus = search_buses_by_number(BUSES, bus_number)
        if bus:
            print("Bot:", respond(
                f"The fare for bus {bus_number} is {bus['fare']}",
                f"Bus {bus_number} ka kiraya {bus['fare']} hai",
                lang
            ))
        else:
            print("Bot:", respond(
                f"Sorry, I couldn’t find bus {bus_number}",
                f"Maaf kijiye, main bus {bus_number} nahi dhoond paaya",
                lang
            ))
        continue

    # -------- Timing ----------
    if intent == "timing_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            print("Bot:", respond(
                "Please provide a bus number to check the timing.",
                "Kirpya bus number bataye taaki main timing bata sakun.",
                lang
            ))
            continue
        bus = search_buses_by_number(BUSES, bus_number)
        if bus:
            print("Bot:", respond(
                f"Bus {bus_number} leaves at {bus['time']}",
                f"Bus {bus_number} {bus['time']} baje nikalti hai",
                lang
            ))
        else:
            print("Bot:", respond(
                f"Sorry, I couldn’t find bus {bus_number}",
                f"Maaf kijiye, main bus {bus_number} nahi dhoond paaya",
                lang
            ))
        continue

    # -------- Tracking ----------
    if intent == "track_bus":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            print("Bot:", respond(
                "Please provide a bus number to track.",
                "Kirpya bus number bataye taaki main bus ko track kar sakun.",
                lang
            ))
            continue
        bus = search_buses_by_number(BUSES, bus_number)
        if bus:
            loc_map = loader.simulate_bus_locations([bus])
            location = loc_map[bus_number]["location"]
            print("Bot:", respond(
                f"Bus {bus_number} is currently near {location}",
                f"Bus {bus_number} abhi {location} ke paas hai",
                lang
            ))
        else:
            print("Bot:", respond(
                f"Sorry, I couldn’t find bus {bus_number}",
                f"Maaf kijiye, main bus {bus_number} nahi dhoond paaya",
                lang
            ))
        continue

    # -------- Route / Next bus / Smart period ----------
    if intent == "route_info":
        src = intent_data.get("source")
        dst = intent_data.get("destination")
        period = intent_data.get("period")
        ask_next = intent_data.get("ask_next", False)

        if not (src and dst):
            print("Bot:", respond(
                "Please specify both source and destination, e.g., 'buses from Delhi to Karnal'",
                "Kirpya source aur destination dono bataye, jaise 'Delhi se Karnal ke buses'",
                lang
            ))
            continue

        if ask_next:
            nb = next_bus_between(BUSES, src, dst)
            if nb:
                print("Bot:", respond(
                    f"Next available bus from {src} to {dst} is {nb['bus_id']} at {nb['time']} with fare {nb['fare']}",
                    f"{src} se {dst} ke liye agla bus {nb['bus_id']} hai jo {nb['time']} baje hai, kiraya {nb['fare']}",
                    lang
                ))
            else:
                print("Bot:", respond(
                    f"I couldn't find the next bus from {src} to {dst}",
                    f"Maaf kijiye, main {src} se {dst} ka agla bus nahi dhoond paaya",
                    lang
                ))
            continue

        if period:
            lb = last_bus_in_period_between(BUSES, src, dst, period)
            if lb:
                print("Bot:", respond(
                    f"The last bus from {src} to {dst} in the {period} is {lb['bus_id']} at {lb['time']}",
                    f"{src} se {dst} ka aakhri bus {period} mein {lb['bus_id']} hai jo {lb['time']} baje hai",
                    lang
                ))
            else:
                matches = buses_between(BUSES, src, dst)
                if matches:
                    times = ", ".join([f'{b["bus_id"]} at {b["time"]}' for b in matches])
                    print("Bot:", respond(
                        f"No specific {period} service. Available buses from {src} to {dst}: {times}",
                        f"{period} mein koi vishesh bus nahi hai. {src} se {dst} ke liye uplabdh bus: {times}",
                        lang
                    ))
                else:
                    print("Bot:", respond(
                        f"No buses found between {src} and {dst}",
                        f"{src} aur {dst} ke beech koi bus nahi mili",
                        lang
                    ))
            continue

        matches = buses_between(BUSES, src, dst)
        if matches:
            for b in matches:
                print("Bot:", respond(
                    f"Bus {b['bus_id']} from {b['source']} to {b['destination']} at {b['time']} fare {b['fare']}",
                    f"Bus {b['bus_id']} {b['source']} se {b['destination']} ke liye {b['time']} baje hai, kiraya {b['fare']}",
                    lang
                ))
        else:
            nb = next_bus_between(BUSES, src, dst)
            if nb:
                print("Bot:", respond(
                    f"No direct listing found. Next available bus from {src} to {dst} is {nb['bus_id']} at {nb['time']}",
                    f"Koi seedha bus nahi mila. {src} se {dst} ka agla bus {nb['bus_id']} hai jo {nb['time']} baje hai",
                    lang
                ))
            else:
                print("Bot:", respond(
                    f"No buses found between {src} and {dst}",
                    f"{src} aur {dst} ke beech koi bus nahi mili",
                    lang
                ))
        continue

    # -------- Delay / On-time status ----------
    if intent == "status_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            print("Bot:", respond(
                "Please provide a bus number to check status.",
                "Kirpya bus number bataye taaki main status de sakun.",
                lang
            ))
            continue
        bus = search_buses_by_number(BUSES, bus_number)
        if not bus:
            print("Bot:", respond(
                f"Sorry, I couldn’t find bus {bus_number}",
                f"Maaf kijiye, main bus {bus_number} nahi dhoond paaya",
                lang
            ))
            continue
        delay = get_bus_delay_minutes(bus_number)
        if delay <= 0:
            print("Bot:", respond(
                f"Bus {bus_number} is on time today",
                f"Bus {bus_number} aaj time par hai",
                lang
            ))
        else:
            print("Bot:", respond(
                f"Bus {bus_number} is running {delay} minutes late today",
                f"Bus {bus_number} aaj {delay} minute late hai",
                lang
            ))
        continue

    # -------- Complaint ----------
    if intent == "lodge_complaint":
        bus_number = intent_data.get("bus_number")
        complaint_text = intent_data.get("complaint_text") or user_input
        if not bus_number:
            print("Bot:", respond(
                "Please mention the bus number in your complaint.",
                "Kirpya apni complaint mein bus number bataye.",
                lang
            ))
            continue
        ticket_id = save_complaint_csv(bus_number, complaint_text)
        print("Bot:", respond(
            f"Your complaint has been logged. Ticket ID: {ticket_id}",
            f"Aapki complaint register kar li gayi hai. Ticket ID: {ticket_id}",
            lang
        ))
        continue

    # -------- Fallback ----------
    bus_num_match = re.search(r"\b\d{2,4}\b", user_input)
    if bus_num_match:
        bus_number = bus_num_match.group()
        bus = search_buses_by_number(BUSES, bus_number)
        if bus:
            print("Bot:", respond(
                f"Bus {bus_number} goes from {bus['source']} to {bus['destination']} at {bus['time']} with fare {bus['fare']}",
                f"Bus {bus_number} {bus['source']} se {bus['destination']} jaati hai {bus['time']} baje, kiraya {bus['fare']}",
                lang
            ))
            continue

    print("Bot:", respond(
        "I'm not sure I understood that. Can you rephrase?",
        "Maaf kijiye, main samajh nahi paya. Kya aap ise dobara keh sakte hain?",
        lang
    ))

