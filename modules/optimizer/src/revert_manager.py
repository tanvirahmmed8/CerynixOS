import json
import os

STATE_FILE = "/var/lib/cerynixos-optimizer/last_state.json"

def save_current_state(state_dict: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state_dict, f)

def load_previous_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def clear_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
