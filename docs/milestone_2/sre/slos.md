# Service Level Objectives (SLOs) and Error Budgets

## Critical Backend Services

| Service | Target SLO | Allowed Downtime (Monthly) | Metric / SLI |
|---------|------------|----------------------------|--------------|
| **Enrollment API** | 99.9% | 43m 49s | Success rate of `/api/v1/enroll` POST requests (HTTP 200/201) |
| **Policy Distribution** | 99.95% | 21m 54s | 99th percentile Latency < 200ms & HTTP 200 |
| **Update Metadata** | 99.9% | 43m 49s | Reachability of CDN `/updates/latest.json` |
| **Audit Ingestion** | 99.5% | 3h 39m | Queue acceptance rate (Events processed vs dropped) |
| **Admin Console** | 99.0% | 7h 18m | Availability of web dashboard |

## Alert Thresholds (The Four Golden Signals)

**1. Latency**
- **Warning:** P99 > 300ms for 5 minutes.
- **Critical (Page):** P99 > 1000ms for 2 minutes.

**2. Traffic**
- **Warning:** Unexpected spike of > 200% baseline traffic over 10 minutes.
- **Critical (Page):** Drop in total traffic to near-zero (indicating edge routing failure).

**3. Errors**
- **Warning:** Error rate > 1% over 10 minutes.
- **Critical (Page):** Error rate > 5% over 5 minutes.

**4. Saturation**
- **Warning:** DB Connection Pool > 75%, CPU > 80% on API nodes.
- **Critical (Page):** Disk space > 90% on Audit DB, CPU > 95% on API nodes.
