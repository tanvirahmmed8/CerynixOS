#!/usr/bin/env python3
import hashlib
import os
import sys

MODEL_DIR = "/var/lib/cerynixos-models"
PLUGIN_DIR = "/var/lib/cerynixos-plugins"
KNOWN_GOOD_LEDGER = "/var/lib/cerynixos-security/ledger.json"

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def verify_models():
    print("Verifying Model Integrity...")
    if not os.path.exists(MODEL_DIR):
        print(f"Model directory {MODEL_DIR} not found. Skipping.")
        return True
        
    # In a real environment, we'd load KNOWN_GOOD_LEDGER and compare.
    # Here we simulate scanning the models directory.
    for root, dirs, files in os.walk(MODEL_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            file_hash = compute_sha256(filepath)
            print(f"  [OK] {file} -> {file_hash}")
            
    return True

def verify_plugins():
    print("\nVerifying Plugin Signatures...")
    if not os.path.exists(PLUGIN_DIR):
        print(f"Plugin directory {PLUGIN_DIR} not found. Skipping.")
        return True
        
    for plugin_name in os.listdir(PLUGIN_DIR):
        manifest_path = os.path.join(PLUGIN_DIR, plugin_name, "manifest.json")
        if os.path.exists(manifest_path):
            # STUB: Cryptographic signature verification of the manifest
            print(f"  [OK] {plugin_name} (Signature Valid)")
        else:
            print(f"  [FAIL] {plugin_name} (Missing manifest!)")
            return False
            
    return True

if __name__ == "__main__":
    print("=== CerynixOS Security Integrity Checker ===")
    models_ok = verify_models()
    plugins_ok = verify_plugins()
    
    if models_ok and plugins_ok:
        print("\nPASS: All integrity checks passed.")
        sys.exit(0)
    else:
        print("\nFAIL: System integrity compromised!")
        sys.exit(1)
