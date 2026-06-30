# CerynixOS Artifact Registry Access Guidelines

This document details the registry architecture, JSON schemas, approval workflows, and client download procedures for system developers and fleet operators.

---

## 1. Registry Architecture & Scope

The CerynixOS Control Plane hosts a cryptographically secure, version-controlled metadata catalog split into three classes of deployment packages:

1. **System Binaries (`system`):** LTS Linux kernel packages, bootloaders, base NixOS profile system configurations, and security services payloads.
2. **AI Models (`model`):** Compact LLM models (primarily `.gguf` formats like the default `qwen2.5-0.5b-instruct-q4_k_m.gguf` runtime model).
3. **Plugins (`plugin`):** Capability extensions, local monitoring daemons, and system agent plugins (e.g. `usbguard`).

---

## 2. Artifact Schema Definition

Every registry artifact register request requires a valid metadata profile matching the [registry-metadata.json](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/contracts/registry-metadata.json) schema:

```json
{
  "artifact_id": "model_qwen25_05b_gguf",
  "name": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "type": "model",
  "version": "1.0.0",
  "description": "Default v1 CerynixAI model payload.",
  "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "file_size_bytes": 390000000,
  "checksum_sha256": "81f1853d9e847c21f2bb8b15d2a84c21f2bb8b15d2a84c21f2bb8b15d2a84c21",
  "download_url": "https://storage.cerynix.internal/registry/models/qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "signature": "cryptographic_developer_signature_block_hex"
}
```

### Signature Field Constraints
The `signature` string verifies developer authenticity. The control plane checks that the binary packages match checksums and verification certificates prior to catalog promotion.

---

## 3. Approved Version Catalog

By default, newly uploaded artifact metadata starts in the `pending` state. Devices cannot view or fetch pending items.

1. **Upload Request (Developer):**
   `POST /api/v1/registry/artifacts` (Authenticated)

2. **Promotion Request (Operator Review):**
   `PATCH /api/v1/registry/artifacts/{artifact_id}/approve` (Authenticated)
   Payload: `{"status": "approved"}`

3. **Catalog Retrieval (Device/Agent):**
   `GET /api/v1/registry/catalog?type=model`
   *Only lists approved items.*

---

## 4. Secure Download URL Signing

To support secure downloads without exposing long-term storage access keys, the control plane generates time-bound signed URLs:

- **Endpoint:** `GET /api/v1/registry/artifacts/{artifact_id}/download`
- **Output:**
  ```json
  {
    "artifact_id": "model_qwen25_05b_gguf",
    "signed_url": "https://storage.cerynix.internal/.../qwen2.5-0.5b-instruct-q4_k_m.gguf?expires=1782800000&signature=a59f1c7d..."
  }
  ```

### Verification Logic
The `signature` parameter is generated via a SHA256 HMAC algorithm over the combination of `artifact_id` and the `expires` timestamp. Device planes verify the signature parameters on download execution.
