# Milestone 3: Consumer Launch, Update Server, and Native UI

## Purpose
This milestone pivots from the Enterprise Control Plane (Milestone 2) to focus on a direct-to-consumer release. It covers building a lightweight static Update Server for Over-The-Air (OTA) updates, a consumer-facing website for downloading the ISO, and resolving the technical debt of the Desktop UI by migrating it to a native GTK application.

## Tracking Legend
* `[ ]` Not started
* `[~]` In progress
* `[x]` Completed

## Done Definition
* A consumer can visit a website, download the CerynixOS ISO, and install it.
* The installed OS automatically checks the Update Server daily and downloads new updates securely.
* The CerynixAI UI is a native GTK window integrated into the GNOME desktop (no open HTTP ports).

---

## Phase 0: Milestone Setup & Architecture
* [x] Define the JSON schema for the OTA update metadata (`latest.json`).
* [x] Select the hosting platform for the Update Server and ISO distribution (e.g., GitHub Pages, AWS S3, or Vercel).
* [x] Design the architecture for the Native GTK CerynixAI app.

## Phase 1: The Update Server & Consumer Website
* [x] Build a simple, beautiful landing page for CerynixOS.
* [x] Implement the static Update Server API (serving OS version metadata and changelogs).
* [x] Set up the CI/CD pipeline to automatically publish new ISO builds to the download server.

## Phase 2: OS Update Agent Integration
* [x] Modify `modules/update-agent/default.nix` to point to the real production Update Server URL.
* [x] Implement cryptographic signature verification for downloaded updates (to prevent tampering).
* [x] Add a user-facing notification when an update is ready to be applied.

## Phase 3: Native GTK UI Redesign (Tech Debt Resolution)
* [x] Deprecate the Python HTTP `ui_server.py`.
* [x] Build a native GTK+WebKit application to host the Glassmorphism UI.
* [x] Build a GNOME Shell Extension to add the CerynixAI icon to the top system bar.
* [x] Ensure the native UI communicates exclusively over the Unix Domain Socket (UDS).

## Phase 4: Launch & Quality Assurance
* [x] Perform end-to-end testing of a full OTA update on a running VM.
* [x] Finalize the "Getting Started" guide for consumers.
* [x] Freeze Milestone 3 and prepare for public Beta release.
