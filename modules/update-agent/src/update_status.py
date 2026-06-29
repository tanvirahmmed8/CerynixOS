#!/usr/bin/env python3
import json
import os

HISTORY_FILE = "/var/lib/cerynixos-update/history.json"

def print_status():
    if not os.path.exists(HISTORY_FILE):
        print("No update history found.")
        return
        
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        
    print(f"{'TIMESTAMP':<25} | {'VERSION':<10} | {'STATUS':<15} | {'MESSAGE'}")
    print("-" * 80)
    for entry in history[-10:]: # Show last 10
        print(f"{entry['timestamp']:<25} | {entry['version']:<10} | {entry['status']:<15} | {entry['message']}")

if __name__ == "__main__":
    print_status()
