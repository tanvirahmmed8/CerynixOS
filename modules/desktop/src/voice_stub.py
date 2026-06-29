import time
import random
import sys

def simulate_voice_pipeline():
    print("[Voice Stub] Initializing local Wake Word engine (Porcupine/Snowboy mock)...")
    print("[Voice Stub] Initializing local STT engine (Whisper.cpp mock)...")
    time.sleep(1)
    print("[Voice Stub] Ready and listening for 'Hey Cerynix'.")
    
    # Mock detection sequence
    try:
        while True:
            time.sleep(random.randint(15, 60))
            print("\n[Voice Stub] Wake word detected!")
            time.sleep(2)
            commands = [
                "Turn on battery saver.",
                "What is my health score?",
                "Update the system."
            ]
            print(f"[Voice Stub] Transcribed: '{random.choice(commands)}'")
            print("[Voice Stub] Forwarding to CerynixAI Action Broker over UDS...")
    except KeyboardInterrupt:
        print("\n[Voice Stub] Shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    simulate_voice_pipeline()
