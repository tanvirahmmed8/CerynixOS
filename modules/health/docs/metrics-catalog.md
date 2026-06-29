# Metrics Catalog

The Local Health Agent collects the following standard metrics to drive the Optimization Engine and calculate the system Health Score.

## Hardware Metrics
- `cpu_load_avg_1m`: 1-minute CPU load average.
- `mem_pressure_pct`: Percentage of available memory currently in use.
- `disk_io_wait_ms`: Average I/O wait time.

## Application Metrics
- `ai_inference_latency_ms`: Time taken for the last inference request.
- `action_broker_exec_count`: Number of actions executed in the last hour.
- `action_broker_deny_count`: Number of actions denied by policy in the last hour.

## Service Metrics
- `service_state_broker`: Active/Inactive state of `cerynix-action-broker`.
- `service_state_inference`: Active/Inactive state of `cerynix-inference-manager`.
