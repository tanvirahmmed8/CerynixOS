# Milestone 1: Device Plane, AI Runtime, and Local OS Experience

## Purpose
This milestone covers the endpoint OS experience: base system, local AI runtime, action broker, optimization engine, self-healing, local observability, plugin runtime, and premium workstation UX foundations.

## Owner Model
* Primary owner: Tanvir
* Work style: Independent delivery with mocked control-plane integrations
* External dependency rule: Do not block on Milestone 2; use local stubs, fixture policies, and fake enrollment tokens where needed

## Tracking Legend
* `[ ]` Not started
* `[~]` In progress
* `[x]` Completed

## Done Definition
* Bootable CerynixOS image exists
* CerynixAI can safely perform bounded actions
* Optimization and self-healing flows work on at least one certified hardware target
* All privileged actions are logged locally
* Device plane can later connect to a real control plane without major refactor

---

## Phase 0: Milestone Setup and Contracts
* [x] Define Milestone 1 scope boundaries and non-goals
* [x] Create device-plane architecture diagram
* [x] Define endpoint service list and ownership map
* [x] Write local interface contracts for:
* [x] Policy fetch format
* [x] Enrollment token format
* [x] Update metadata format
* [x] Audit event schema
* [x] Health report schema
* [x] Create mock services and fixture files for all remote contracts
* [x] Define local development workflow for image build, run, rollback, and log collection
* [x] Establish coding standards, repo folders, and naming rules for device services

## Phase 1: Base OS Foundation
* [x] Set up NixOS flake structure for CerynixOS
* [x] Create base system modules for common packages and services
* [x] Define hardware profiles for first target devices
* [x] Configure boot flow and system defaults
* [x] Configure immutable/declarative system management patterns
* [x] Create reproducible image build pipeline for:
* [x] VM image
* [x] Installer ISO
* [x] Bare metal test image
* [x] Add rollback-safe system generation workflow
* [x] Add baseline package set for developer workstation profile
* [x] Add baseline package set for creator workstation profile
* [x] Document local image build and flash process

## Phase 2: Local AI Runtime Foundation
* [x] Lock `llama.cpp` as the primary local inference engine for v1
* [x] Select optional accelerated inference path for high-end hardware
* [x] Package `qwen2.5-0.5b-instruct-q4_k_m.gguf` as the default v1 assistant model
* [x] Define model packaging layout and versioning
* [x] Build local model loader service
* [x] Build inference manager with:
* [x] Model selection rules
* [x] Memory budget enforcement
* [x] Timeout handling
* [x] Fallback behavior
* [x] Add default model config for `qwen2.5-0.5b-instruct-q4_k_m.gguf`
* [x] Secure API via Unix Domain Socket (UDS) instead of TCP to prevent port collisions
* [x] Add prompt templating layer for OS tasks
* [x] Add local task memory storage with retention limits
* [x] Add privacy mode to disable memory persistence
* [x] Create benchmark suite for inference latency and memory usage
* [x] Validate runtime behavior of `qwen2.5-0.5b-instruct-q4_k_m.gguf` on minimum supported hardware

## Phase 3: Action Broker and Safe Execution Layer
* [x] Define capability model for privileged and non-privileged actions
* [x] Define allowed tool categories:
* [x] File operations
* [x] Process operations
* [x] Package/config operations
* [x] Service control
* [x] Desktop automation
* [x] Build action broker service
* [x] Add explicit approval modes:
* [x] Suggest-only
* [x] Ask-before-act
* [x] Auto-act within policy
* [x] Add command validation and argument sanitization
* [x] Add execution timeout and cancellation handling
* [x] Add structured result reporting
* [x] Add policy-driven deny list and allow list support
* [x] Add rollback hook support for mutating actions
* [x] Add audit event emission for all executed actions
* [x] Write integration tests for safe execution boundaries

## Phase 4: Local Observability and Diagnostics
* [x] Define local metrics catalog for device services
* [x] Define structured log format across all device components
* [x] Implement local health agent
* [x] Implement service heartbeat checks
* [x] Add crash capture and error bundle generation
* [x] Add local diagnostics CLI
* [x] Add local health score calculation
* [x] Add troubleshooting snapshot export
* [x] Add redaction rules for sensitive diagnostics content
* [x] Validate low-overhead observability behavior

## Phase 5: Optimization Engine v1
* [x] Define measurable optimization targets:
* [x] CPU responsiveness
* [x] Memory pressure recovery
* [x] I/O prioritization
* [x] Thermal stability
* [x] Battery efficiency
* [x] Implement real-time telemetry collector for optimization inputs
* [x] Implement rule-based optimization engine
* [x] Create workload profiles:
* [x] Coding
* [x] Gaming
* [x] Conferencing
* [x] Rendering
* [x] Battery saver
* [x] Add explainability layer for optimization decisions
* [x] Add one-click revert for profile and tuning changes
* [x] Add hardware override tables for known devices
* [x] Create before/after performance benchmark suite
* [x] Validate optimization gains against baseline system image

## Phase 6: Self-Healing and Recovery v1
* [ ] Define supported failure scenarios for v1:
* [ ] Failed update rollback
* [ ] Broken user configuration recovery
* [ ] Common service restart failures
* [ ] Package/config drift detection
* [ ] Storage pressure cleanup suggestions
* [ ] Build drift detection service
* [ ] Build known-good state snapshot and restore flow
* [ ] Add automatic rollback rules for safe scenarios
* [ ] Add guided recovery UI for medium-confidence scenarios
* [ ] Add recovery logs and user-facing explanation messages
* [ ] Write scenario-based recovery tests
* [ ] Validate no destructive recovery action occurs without policy allowance

## Phase 7: Desktop UX and CerynixAI Experience
* [ ] Select desktop base: KDE or GNOME
* [ ] Create CerynixOS shell branding and theme foundations
* [ ] Build CerynixAI panel or overlay UI
* [ ] Build text-first CerynixAI workflow
* [ ] Add optional voice pipeline stub with local/offline-first path
* [ ] Add action confirmation UX patterns
* [ ] Add optimization dashboard UI
* [ ] Add self-healing status UI
* [ ] Add local privacy controls UI
* [ ] Add accessibility pass for core assistant surfaces
* [ ] Validate UX on laptop and desktop layouts

## Phase 8: Update Agent and Local Release Safety
* [ ] Build local update agent
* [ ] Implement update metadata parser using fixture contracts
* [ ] Add staged update application flow
* [ ] Add pre-update health checks
* [ ] Add post-update verification checks
* [ ] Add failed-update automatic rollback
* [ ] Add user-facing update status and history
* [ ] Write update simulation tests with mock metadata

## Phase 9: Plugin Runtime and Developer Extensibility
* [ ] Define plugin packaging contract for device-side skills/tools
* [ ] Implement plugin discovery flow
* [ ] Implement plugin permission model
* [ ] Implement plugin isolation and failure handling
* [ ] Add plugin lifecycle management:
* [ ] Install
* [ ] Disable
* [ ] Upgrade
* [ ] Remove
* [ ] Add developer sample plugin
* [ ] Add plugin test harness
* [ ] Add plugin audit and telemetry hooks

## Phase 10: Security Hardening on Device
* [ ] Enable disk encryption baseline
* [ ] Add secure secret storage integration
* [ ] Add device identity placeholder flow for future TPM-backed enrollment
* [ ] Harden local service permissions
* [ ] Validate sandbox boundaries between assistant, broker, and plugins
* [ ] Add model file integrity verification
* [ ] Add plugin signature verification stub support
* [ ] Review local attack surface and close obvious privilege-escalation paths

## Phase 11: Quality, Certification, and Milestone Exit
* [ ] Create milestone test matrix by hardware class
* [ ] Run install tests in VM and on target hardware
* [ ] Run resource stress tests
* [ ] Run rollback and recovery tests
* [ ] Run AI task safety regression tests
* [ ] Run UX acceptance checklist
* [ ] Freeze milestone scope
* [ ] Publish Milestone 1 demo notes and operator guide
* [ ] Document open issues, technical debt, and interfaces for Milestone 2 integration

---

## Parallelization Notes
* Milestone 1 should never wait for the real fleet backend
* Every remote-facing function must have a local mock
* Contract files should be versioned early and changed carefully
* If a real control-plane API is not ready, continue using fixtures and adapter interfaces

## Milestone Exit Deliverables
* [ ] Bootable CerynixOS image
* [ ] Device service architecture document
* [ ] Local AI runtime and action broker
* [ ] Optimization engine v1
* [ ] Self-healing v1
* [ ] CerynixAI UI
* [ ] Local observability and diagnostics tools
* [ ] Update agent with rollback
* [ ] Plugin runtime v1
* [ ] Milestone validation report
