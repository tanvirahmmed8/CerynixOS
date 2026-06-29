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
* Local AI assistant can safely perform bounded actions
* Optimization and self-healing flows work on at least one certified hardware target
* All privileged actions are logged locally
* Device plane can later connect to a real control plane without major refactor

---

## Phase 0: Milestone Setup and Contracts
* [ ] Define Milestone 1 scope boundaries and non-goals
* [ ] Create device-plane architecture diagram
* [ ] Define endpoint service list and ownership map
* [ ] Write local interface contracts for:
* [ ] Policy fetch format
* [ ] Enrollment token format
* [ ] Update metadata format
* [ ] Audit event schema
* [ ] Health report schema
* [ ] Create mock services and fixture files for all remote contracts
* [ ] Define local development workflow for image build, run, rollback, and log collection
* [ ] Establish coding standards, repo folders, and naming rules for device services

## Phase 1: Base OS Foundation
* [ ] Set up NixOS flake structure for CerynixOS
* [ ] Create base system modules for common packages and services
* [ ] Define hardware profiles for first target devices
* [ ] Configure boot flow and system defaults
* [ ] Configure immutable/declarative system management patterns
* [ ] Create reproducible image build pipeline for:
* [ ] VM image
* [ ] Installer ISO
* [ ] Bare metal test image
* [ ] Add rollback-safe system generation workflow
* [ ] Add baseline package set for developer workstation profile
* [ ] Add baseline package set for creator workstation profile
* [ ] Document local image build and flash process

## Phase 2: Local AI Runtime Foundation
* [ ] Select primary local inference engine for low-to-mid hardware
* [ ] Select optional accelerated inference path for high-end hardware
* [ ] Define model packaging layout and versioning
* [ ] Build local model loader service
* [ ] Build inference manager with:
* [ ] Model selection rules
* [ ] Memory budget enforcement
* [ ] Timeout handling
* [ ] Fallback behavior
* [ ] Add prompt templating layer for OS tasks
* [ ] Add local task memory storage with retention limits
* [ ] Add privacy mode to disable memory persistence
* [ ] Create benchmark suite for inference latency and memory usage
* [ ] Validate runtime behavior on minimum supported hardware

## Phase 3: Action Broker and Safe Execution Layer
* [ ] Define capability model for privileged and non-privileged actions
* [ ] Define allowed tool categories:
* [ ] File operations
* [ ] Process operations
* [ ] Package/config operations
* [ ] Service control
* [ ] Desktop automation
* [ ] Build action broker service
* [ ] Add explicit approval modes:
* [ ] Suggest-only
* [ ] Ask-before-act
* [ ] Auto-act within policy
* [ ] Add command validation and argument sanitization
* [ ] Add execution timeout and cancellation handling
* [ ] Add structured result reporting
* [ ] Add policy-driven deny list and allow list support
* [ ] Add rollback hook support for mutating actions
* [ ] Add audit event emission for all executed actions
* [ ] Write integration tests for safe execution boundaries

## Phase 4: Local Observability and Diagnostics
* [ ] Define local metrics catalog for device services
* [ ] Define structured log format across all device components
* [ ] Implement local health agent
* [ ] Implement service heartbeat checks
* [ ] Add crash capture and error bundle generation
* [ ] Add local diagnostics CLI
* [ ] Add local health score calculation
* [ ] Add troubleshooting snapshot export
* [ ] Add redaction rules for sensitive diagnostics content
* [ ] Validate low-overhead observability behavior

## Phase 5: Optimization Engine v1
* [ ] Define measurable optimization targets:
* [ ] CPU responsiveness
* [ ] Memory pressure recovery
* [ ] I/O prioritization
* [ ] Thermal stability
* [ ] Battery efficiency
* [ ] Implement real-time telemetry collector for optimization inputs
* [ ] Implement rule-based optimization engine
* [ ] Create workload profiles:
* [ ] Coding
* [ ] Gaming
* [ ] Conferencing
* [ ] Rendering
* [ ] Battery saver
* [ ] Add explainability layer for optimization decisions
* [ ] Add one-click revert for profile and tuning changes
* [ ] Add hardware override tables for known devices
* [ ] Create before/after performance benchmark suite
* [ ] Validate optimization gains against baseline system image

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

## Phase 7: Desktop UX and Assistant Experience
* [ ] Select desktop base: KDE or GNOME
* [ ] Create CerynixOS shell branding and theme foundations
* [ ] Build assistant panel or overlay UI
* [ ] Build text-first assistant workflow
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
* [ ] Desktop assistant UI
* [ ] Local observability and diagnostics tools
* [ ] Update agent with rollback
* [ ] Plugin runtime v1
* [ ] Milestone validation report
