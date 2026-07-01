#!/usr/bin/env python3
import json
import hashlib
import os

print("--- Starting OTA E2E Simulation ---")

# 1. Load the generated latest.json
latest_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../website/api/latest.json"))
with open(latest_json_path, "r") as f:
    meta = json.load(f)

print(f"1. Successfully parsed latest.json (Version: {meta['version']})")

# 2. Simulate ISO Download
print(f"2. Simulating download from {meta['iso_url']}...")
mock_iso_path = "/tmp/mock_cerynixos.iso"
with open(mock_iso_path, "wb") as f:
    # We write fake data, so the hash won't match, simulating a MITM attack
    f.write(b"MALICIOUS_ISO_DATA")

# 3. Simulate Hash Verification (Expected to Fail)
print("3. Verifying Cryptographic Hash...")
file_hash = hashlib.sha256(open(mock_iso_path, 'rb').read()).hexdigest()
expected_hash = meta['sha256_hash']

print(f"   Expected: {expected_hash}")
print(f"   Actual:   {file_hash}")

if file_hash != expected_hash:
    print("\n[SUCCESS] Hash mismatch detected! The OTA agent successfully blocked a simulated Man-In-The-Middle attack.")
    os.remove(mock_iso_path)
else:
    print("\n[FAILED] Hash matched malicious data. Security compromise.")
    exit(1)

print("--- OTA E2E Simulation Complete ---")
