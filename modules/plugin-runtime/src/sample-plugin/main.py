#!/usr/bin/env python3
import json
import sys

def main():
    # A real plugin might use 'requests' to hit an API based on sys.argv[1]
    location = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # Must output valid JSON for the AI
    output = {
        "status": "success",
        "location": location,
        "temperature_c": 22,
        "condition": "Sunny",
        "note": "This is data from the sample plugin running in an isolated shell."
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
