# Incident Response Runbooks

## 1. Enrollment Failure (Identity Verification Timeout)
**Trigger:** High failure rate on `/api/v1/enroll` endpoints.
**Impact:** New laptops cannot be provisioned or join the fleet.
**Resolution Steps:**
1. Check TPM Attestation service health in Grafana.
2. Verify Root CA certificate validity (Has it expired?).
3. If the backend cannot reach the Certificate Authority, route traffic to the fallback CA replica.
4. Escalate to Identity/IAM team if TPM quote verification is failing continuously.

## 2. Policy Publication Failure
**Trigger:** Policies created in Admin Console are not propagating to devices (MQTT/Webhook failures).
**Impact:** Devices are running stale security policies.
**Resolution Steps:**
1. Check the background job queue (e.g., Redis/Celery).
2. If queue is backed up, scale up the `policy-worker` instances.
3. Check database locks on the `policies` table. Terminate stalled queries if necessary.
4. Notify Fleet Admins that policy sync is degraded.

## 3. Update Campaign Failure
**Trigger:** Devices report HTTP 503 or Checksum Mismatches when fetching OTA metadata.
**Impact:** Devices cannot download security patches.
**Resolution Steps:**
1. Validate the `latest.json` syntax and SRI hashes in the S3 bucket.
2. Check CDN Edge cache hit rate. Purge CDN cache if bad metadata was served.
3. If the backend update API is down, failover to the static S3 replica.

## 4. Audit Pipeline Degradation
**Trigger:** Audit events (from Action Broker) are being dropped or returning HTTP 429.
**Impact:** Loss of compliance tracking and security auditing.
**Resolution Steps:**
1. This is a non-critical flow for device operation, but critical for compliance.
2. If the primary Audit DB is slow, ensure the API is pushing to an intermediate message queue (Kafka/RabbitMQ) instead of writing directly to the DB.
3. If the queue is full, dynamically increase the retention size and scale consumers.

## 5. Database Capacity Issue
**Trigger:** DB Disk > 90% or CPU > 95%.
**Impact:** Complete Control Plane outage.
**Resolution Steps:**
1. Check active connections. Identify runaway queries using `pg_stat_activity`.
2. For disk space, execute emergency log rotation or archival of the `audit_events` table (move older than 30 days to cold storage).
3. Increase storage volume size (if on cloud managed DB like RDS) — requires zero downtime.
