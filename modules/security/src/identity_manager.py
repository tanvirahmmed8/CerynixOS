#!/usr/bin/env python3
import os
import json
import uuid
import datetime

KEYSTORE_DIR = "/var/lib/cerynixos-security/identity"

def generate_mock_identity():
    print("Initializing TPM Mock Identity Generator...")
    os.makedirs(KEYSTORE_DIR, exist_ok=True)
    
    identity_file = os.path.join(KEYSTORE_DIR, "device_identity.json")
    
    if os.path.exists(identity_file):
        print("Device is already enrolled. Identity exists.")
        with open(identity_file, "r") as f:
            identity = json.load(f)
            print(f"Device ID: {identity.get('device_id')}")
        return
        
    print("Generating new hardware-bound identity...")
    identity = {
        "device_id": str(uuid.uuid4()),
        "enrolled_at": datetime.datetime.utcnow().isoformat() + "Z",
        "tpm_attestation_mock": "x509_cert_stub_data_1234567890",
        "status": "pending_fleet_registration"
    }
    
    # Store securely (restrict permissions)
    with open(identity_file, "w") as f:
        json.dump(identity, f, indent=2)
        
    os.chmod(identity_file, 0o600)
    
    print("Successfully generated mock TPM identity.")
    print(f"Device ID: {identity['device_id']}")
    print("Ready for Milestone 2 Control Plane integration.")

if __name__ == "__main__":
    generate_mock_identity()
