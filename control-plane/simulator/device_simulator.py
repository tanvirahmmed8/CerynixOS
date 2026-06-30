#!/usr/bin/env python3
import json
import os
import uuid
from datetime import datetime, timezone

# Path definitions relative to workspace root
CONTRACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../contracts"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))

def load_schema(filename):
    path = os.path.join(CONTRACTS_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)

# A simple JSON Schema validator using Python standard library
def validate_json(instance, schema, path=""):
    # Check type
    expected_type = schema.get("type")
    if expected_type:
        if expected_type == "string":
            if not isinstance(instance, str):
                raise TypeError(f"Validation failed at '{path}': Expected string, got {type(instance).__name__}")
        elif expected_type == "integer":
            if not isinstance(instance, int) or isinstance(instance, bool):
                raise TypeError(f"Validation failed at '{path}': Expected integer, got {type(instance).__name__}")
        elif expected_type == "boolean":
            if not isinstance(instance, bool):
                raise TypeError(f"Validation failed at '{path}': Expected boolean, got {type(instance).__name__}")
        elif expected_type == "array":
            if not isinstance(instance, list):
                raise TypeError(f"Validation failed at '{path}': Expected array/list, got {type(instance).__name__}")
            # Validate items if schema defines them
            items_schema = schema.get("items")
            if items_schema:
                for idx, item in enumerate(instance):
                    validate_json(item, items_schema, f"{path}[{idx}]")
        elif expected_type == "object":
            if not isinstance(instance, dict):
                raise TypeError(f"Validation failed at '{path}': Expected object/dict, got {type(instance).__name__}")
            # Check required fields
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in instance:
                    raise KeyError(f"Validation failed at '{path}': Missing required field '{field}'")
            # Validate properties
            properties = schema.get("properties", {})
            for key, val in instance.items():
                if key in properties:
                    validate_json(val, properties[key], f"{path}.{key}" if path else key)

    # Check minimum/maximum for integers
    if isinstance(instance, int) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            raise ValueError(f"Validation failed at '{path}': Value {instance} is less than minimum {minimum}")
        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            raise ValueError(f"Validation failed at '{path}': Value {instance} is greater than maximum {maximum}")

    # Check enum
    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        raise ValueError(f"Validation failed at '{path}': Value '{instance}' is not in allowed enum {enum}")

    return True

# Payload Generators
def generate_enrollment_token():
    return {
        "token": "tok_cerynix_enroll_1a2b3c4d5e",
        "organization_id": "org_enterprise_alpha",
        "endpoint": "https://control-plane.cerynix.internal/api/v1/enroll"
    }

def generate_device_inventory(device_id):
    return {
        "device_id": device_id,
        "device_model": "ThinkPad P1 Gen 6",
        "os_version": "cerynixos-gen-42",
        "hardware_profile": {
            "cpu_cores": 14,
            "memory_bytes": 34359738368,  # 32 GB
            "storage_bytes": 1099511627776  # 1 TB
        },
        "installed_capabilities": [
            "cerynix-base",
            "cerynix-ai-runtime",
            "cerynix-action-broker",
            "cerynix-health-agent",
            "cerynix-optimizer",
            "cerynix-healer"
        ],
        "enrollment_state": "active",
        "tags": ["developer", "milestone-2-pilot"],
        "group_id": "grp_dev_workstations"
    }

def generate_policy_fetch():
    return {
        "policy_id": "pol_strict_dev_v2",
        "version": 5,
        "rules": {
            "allowed_tools": [
                "systemctl status",
                "journalctl",
                "nixos-rebuild dry-run",
                "cerynix-optimizer apply"
            ],
            "approval_mode": "ask_before_act"
        }
    }

def generate_health_report(device_id):
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_score": 95,
        "components": {
            "cpu": "healthy",
            "memory": "healthy",
            "storage": "healthy",
            "services": "healthy"
        }
    }

def generate_audit_event():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "cerynix-action-broker",
        "action": "run_tool: cerynix-optimizer apply gaming",
        "status": "success",
        "details": {
            "arguments": ["gaming"],
            "operator": "cerynix-ai-assistant",
            "approval_level": "suggest_only"
        }
    }

def generate_update_metadata():
    return {
        "version": "cerynixos-gen-43",
        "channel": "pilot",
        "image_url": "https://registry.cerynix.internal/images/cerynixos-gen-43.iso",
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "force_rollback": False
    }

def generate_support_bundle(device_id):
    return {
        "device_id": device_id,
        "bundle_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bundle_size_bytes": 10485760,  # 10 MB
        "bundle_url": "file:///var/lib/cerynixos-support/bundle-active.tar.gz",
        "trigger_reason": "operator_request",
        "redaction_applied": True,
        "metadata": {
            "reported_health_score": "95",
            "triggering_user": "avishek"
        }
    }

def main():
    print("==================================================")
    print("CerynixOS Fleet Device Simulator & Contract Verifier")
    print("==================================================")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    device_id = str(uuid.uuid4())
    
    test_cases = [
        ("enrollment-token.json", generate_enrollment_token(), "enrollment_token.json"),
        ("device-inventory.json", generate_device_inventory(device_id), "device_inventory.json"),
        ("policy-fetch.json", generate_policy_fetch(), "policy_fetch.json"),
        ("health-report.json", generate_health_report(device_id), "health_report.json"),
        ("audit-event.json", generate_audit_event(), "audit_event.json"),
        ("update-metadata.json", generate_update_metadata(), "update_metadata.json"),
        ("support-bundle.json", generate_support_bundle(device_id), "support_bundle.json")
    ]
    
    success_count = 0
    for schema_file, payload, output_file in test_cases:
        print(f"\nProcessing schema: {schema_file}")
        try:
            schema = load_schema(schema_file)
            validate_json(payload, schema)
            print(f"  [PASS] Payload matches schema perfectly.")
            
            # Save generated payload to output dir
            out_path = os.path.join(OUTPUT_DIR, output_file)
            with open(out_path, "w") as f:
                json.dump(payload, f, indent=2)
            print(f"  [INFO] Saved valid sample to: {os.path.relpath(out_path)}")
            success_count += 1
        except Exception as e:
            print(f"  [FAIL] Validation error: {str(e)}")
            
    print("\n==================================================")
    print(f"Verification Summary: {success_count}/{len(test_cases)} passed.")
    print("==================================================")
    
    if success_count == len(test_cases):
        print("Success! All payload contracts are verified and frozen.")
        return 0
    else:
        print("Failure! Some contracts failed verification.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
