# Mock Services Strategy

During Milestone 1, the device plane operates without a real enterprise control plane. To ensure our endpoint services are built correctly and can be seamlessly integrated with the real control plane in Milestone 2, we use local mock fixtures.

## How it works
All device services that would normally make HTTP/gRPC calls to the control plane must instead implement an interface that can read from or write to the JSON fixtures in the `fixtures/` directory.

- **Fetching Policy:** `cerynix-policy-agent` reads `fixtures/sample-policy.json`.
- **Enrollment:** The system uses `fixtures/sample-enrollment-token.json`.
- **Updates:** `cerynix-update-agent` polls `fixtures/sample-update-metadata.json`.
- **Telemetry/Logs:** Instead of sending to a remote ingestor, they are logged locally (or optionally appended to `fixtures/sample-health-report.json` or `fixtures/sample-audit-event.json` for validation).

When Milestone 2 begins, we will simply swap the local file adapter with a network adapter, leaving the core business logic of the device services untouched.
