# Structured Log Format

All CerynixOS device-plane services MUST emit logs to `stdout` in the following JSON format. This ensures seamless ingestion by `journald` and easy parsing by the local health agent.

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp."
    },
    "level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
    },
    "service": {
      "type": "string",
      "description": "The name of the emitting service (e.g., cerynix-action-broker)."
    },
    "message": {
      "type": "string",
      "description": "Human readable log message."
    },
    "context": {
      "type": "object",
      "description": "Key-value pairs for structured querying (e.g., user_id, action, latency)."
    }
  },
  "required": ["timestamp", "level", "service", "message"]
}
```
