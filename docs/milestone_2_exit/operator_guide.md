# CerynixOS Control Plane - Operator Guide

Welcome to the CerynixOS Fleet Management console. This guide explains how to perform daily administrative actions.

## 1. Enrolling a Device
Devices running CerynixOS automatically attempt to enroll when first connected to the network via their TPM module.
1. Navigate to **Fleet > Pending Devices**.
2. Review the hardware attestation signature and the employee assignment.
3. Click **Approve**. The device will be issued a Client Certificate and moved to the Active Fleet, triggering an initial policy sync.

## 2. Pushing a Security Policy
Security policies define what the on-device AI (CerynixAI) is allowed to execute.
1. Navigate to **Policies > Create New**.
2. Select the target (e.g., `All Devices` or `Engineering Group`).
3. Define the rules in the JSON editor (e.g., `"network.firewall.ssh": "deny"`).
4. Set the Policy Weight (higher weight overrides lower weights).
5. Click **Publish**. Devices will sync this policy within 60 seconds.

## 3. Managing OS Updates
CerynixOS uses atomic OTA updates.
1. Navigate to **Updates > Campaigns**.
2. Select the target OS version (e.g., `v1.2.0-stable`).
3. Select the rollout strategy (e.g., `Canary: 5% initially, then 100% after 24 hours`).
4. Click **Start Campaign**. The dashboard will show real-time progress as devices download and reboot into the new generation.
5. *Emergency Rollback:* If the new OS version introduces a bug, click **Halt & Revert**. The devices will use `systemd-boot` to reboot into their previous safe generation.

## 4. Approving AI Plugins
By default, the CerynixAI local model cannot execute any third-party code.
1. Navigate to **Registry > Pending Plugins**.
2. Review the manifest, requested permissions, and source code hash.
3. Click **Sign & Approve**. The Control Plane will cryptographically sign the plugin, allowing devices to safely execute it in the sandboxed `cerynix-plugin-user` environment.
