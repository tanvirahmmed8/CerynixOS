# Changelog - Health Module

## 2026-06-29
- **Feature:** Initial Observability setup
- **Changes:**
  - Created `health_agent` python daemon running every 60 seconds.
  - Implemented health score calculation (CPU, Memory, Service state).
  - Created `cerynix-diag` CLI for status and snapshot generation.
  - Implemented basic regex redaction rules for diagnostics snapshot export.
  - Defined metrics catalog and structured JSON log format.
