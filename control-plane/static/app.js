// State variables
let authToken = localStorage.getItem("cerynix_auth_token") || "";
let activeTab = "overview";
let alertPollInterval = null;

// DOM Elements
const authModal = document.getElementById("auth-modal");
const consoleLayout = document.getElementById("console-layout");
const tokenInput = document.getElementById("token-input");
const authBtn = document.getElementById("auth-btn");
const authError = document.getElementById("auth-error");
const logoutBtn = document.getElementById("logout-btn");
const pageTitle = document.getElementById("page-title");
const navItems = document.querySelectorAll(".nav-menu .nav-item");

// Helper: HTTP Headers with Token
function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
    };
}

// API Call Wrapper
async function apiCall(url, method = "GET", body = null) {
    const options = {
        method,
        headers: getHeaders()
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    
    if (response.status === 401) {
        // Auth expired or invalid
        handleLogout();
        throw new Error("Unauthorized access. Token invalid.");
    }
    
    if (!response.ok) {
        let errText = "API request failed";
        try {
            const errData = await response.json();
            errText = errData.detail || errText;
        } catch {}
        throw new Error(errText);
    }
    
    if (response.status === 204) {
        return null;
    }
    return response.json();
}

// Authentication handlers
authBtn.addEventListener("click", async () => {
    const token = tokenInput.value.trim();
    if (!token) {
        authError.textContent = "Please enter an access token.";
        return;
    }
    
    authError.textContent = "";
    authToken = token;
    
    try {
        // Verify token by querying fleet stats (requires admin role verification)
        await apiCall("/api/v1/observability/fleet");
        localStorage.setItem("cerynix_auth_token", token);
        authModal.classList.add("display-none");
        consoleLayout.classList.remove("layout-hidden");
        
        // Success: Start polling and load active tab
        startAlertsPolling();
        switchTab(activeTab);
    } catch (e) {
        authToken = "";
        authError.textContent = `Verification failed: ${e.message}`;
    }
});

logoutBtn.addEventListener("click", handleLogout);

function handleLogout() {
    authToken = "";
    localStorage.removeItem("cerynix_auth_token");
    consoleLayout.classList.add("layout-hidden");
    authModal.classList.remove("display-none");
    stopAlertsPolling();
}

// Tab Switching Controls
navItems.forEach(item => {
    item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.getAttribute("data-tab");
        switchTab(tab);
    });
});

function switchTab(tabId) {
    activeTab = tabId;
    
    // Toggle active link styles
    navItems.forEach(item => {
        if (item.getAttribute("data-tab") === tabId) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });
    
    // Hide all panes and show target
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });
    const targetPane = document.getElementById(`tab-${tabId}`);
    if (targetPane) {
        targetPane.classList.add("active");
    }
    
    // Update Page Header Title
    pageTitle.textContent = getTabTitle(tabId);
    
    // Trigger tab-specific load functions
    loadTabData(tabId);
}

function getTabTitle(tabId) {
    const titles = {
        overview: "Overview Dashboard",
        inventory: "Fleet Device Inventory",
        policies: "Configuration Policies",
        updates: "Releases & Update Campaigns",
        governance: "Security Governance & Compliance",
        diagnostics: "Diagnostics Console & Incidents",
        simulators: "Synthetic Failure Simulators"
    };
    return titles[tabId] || "Dashboard";
}

// Tab Data Loader Router
function loadTabData(tabId) {
    if (!authToken) return;
    
    switch (tabId) {
        case "overview":
            loadOverviewMetrics();
            break;
        case "inventory":
            loadInventoryDevices();
            break;
        case "policies":
            loadPoliciesWorkspace();
            break;
        case "updates":
            loadUpdatesWorkspace();
            break;
        case "governance":
            // Managed on button click or direct evidence view
            break;
        case "diagnostics":
            loadDiagnosticsWorkspace();
            break;
        case "simulators":
            loadSimulatorsWorkspace();
            break;
    }
}

// --- TAB: OVERVIEW ---
async function loadOverviewMetrics() {
    try {
        const fleetHealth = await apiCall("/api/v1/observability/fleet");
        const alerts = await apiCall("/api/v1/observability/alerts");
        
        // Set metrics values
        document.getElementById("metric-devices").textContent = fleetHealth.total_active_devices;
        document.getElementById("metric-health-score").textContent = `${fleetHealth.average_health_score || 100}%`;
        
        // Count non-compliant devices
        const compliance = await apiCall("/api/v1/compliance/posture");
        document.getElementById("metric-non-compliant").textContent = compliance.non_compliant_count;
        document.getElementById("metric-active-alerts").textContent = alerts.length;
        
        // Health state breakdowns
        const total = fleetHealth.total_active_devices || 1;
        document.getElementById("health-count-healthy").textContent = `${fleetHealth.healthy_count} Devices`;
        document.getElementById("health-pct-healthy").textContent = `${Math.round((fleetHealth.healthy_count / total) * 100)}%`;
        
        document.getElementById("health-count-degraded").textContent = `${fleetHealth.degraded_count} Devices`;
        document.getElementById("health-pct-degraded").textContent = `${Math.round((fleetHealth.degraded_count / total) * 100)}%`;
        
        document.getElementById("health-count-critical").textContent = `${fleetHealth.critical_count} Devices`;
        document.getElementById("health-pct-critical").textContent = `${Math.round((fleetHealth.critical_count / total) * 100)}%`;
        
        // Load Alerts Queue list
        const alertsList = document.getElementById("overview-alerts-list");
        if (alerts.length === 0) {
            alertsList.innerHTML = '<div class="alert-item">No active operational alerts. Fleet is healthy.</div>';
        } else {
            alertsList.innerHTML = alerts.map(alert => `
                <div class="alert-item ${alert.severity}">
                    <div class="alert-header">
                        <span class="alert-title text-${alert.severity}">${alert.alert_type}</span>
                        <span class="alert-time">${formatTimestamp(alert.timestamp)}</span>
                    </div>
                    <span class="alert-msg">${alert.message}</span>
                </div>
            `).join("");
        }
        
        // Update header alerts badge count
        document.getElementById("alerts-count").textContent = alerts.length;
    } catch (e) {
        console.error("Failed to load overview metrics", e);
    }
}

// --- TAB: INVENTORY ---
async function loadInventoryDevices() {
    const tbody = document.getElementById("inventory-table-body");
    tbody.innerHTML = '<tr><td colspan="7" class="text-center">Loading devices...</td></tr>';
    
    try {
        const state = document.getElementById("inventory-filter-state").value;
        const channel = document.getElementById("inventory-filter-channel").value;
        const query = document.getElementById("inventory-search").value.trim();
        
        let url = "/api/v1/devices?";
        if (state) url += `state=${state}&`;
        if (channel) url += `channel=${channel}&`;
        if (query) url += `query=${query}&`;
        
        const devices = await apiCall(url);
        if (devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No matching devices found in inventory.</td></tr>';
            return;
        }
        
        tbody.innerHTML = devices.map(dev => `
            <tr>
                <td><strong>${dev.device_id}</strong></td>
                <td>${dev.device_model}</td>
                <td><span class="badge-state ${dev.enrollment_state}">${dev.enrollment_state}</span></td>
                <td><span class="font-mono">${dev.os_version}</span></td>
                <td><span class="badge-role">${dev.release_channel || "broad"}</span></td>
                <td>${(dev.tags || []).map(t => `<span class="tag">${t}</span>`).join("")}</td>
                <td>
                    <button class="btn-action" onclick="viewDeviceDetails('${dev.device_id}')">Inspect</button>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-critical">Failed to load inventory: ${e.message}</td></tr>`;
    }
}

document.getElementById("inventory-search-btn").addEventListener("click", loadInventoryDevices);
document.getElementById("inventory-filter-state").addEventListener("change", loadInventoryDevices);
document.getElementById("inventory-filter-channel").addEventListener("change", loadInventoryDevices);

async function viewDeviceDetails(deviceId) {
    // Navigate SRE or Technician directly to Diagnostics/Timeline
    switchTab("diagnostics");
    setTimeout(() => {
        document.getElementById("diag-target-device").value = deviceId;
        loadDeviceTimelineDetails(deviceId);
    }, 200);
}

// --- TAB: POLICIES ---
async function loadPoliciesWorkspace() {
    const listContainer = document.getElementById("policies-list-container");
    const policySelect = document.getElementById("assign-policy-id");
    
    listContainer.innerHTML = '<div class="loading-placeholder">Loading policies...</div>';
    
    try {
        const policies = await apiCall("/api/v1/policies");
        
        // Populating targets selector
        policySelect.innerHTML = '<option value="">Choose Policy...</option>' + 
            policies.map(p => `<option value="${p.policy_id}">${p.policy_id}</option>`).join("");
            
        if (policies.length === 0) {
            listContainer.innerHTML = '<div class="loading-placeholder">No policies registered.</div>';
            return;
        }
        
        listContainer.innerHTML = policies.map(p => `
            <div class="policy-item-card">
                <div class="policy-header">
                    <span class="policy-id">🛡️ ${p.policy_id}</span>
                    <span class="user-org">Rev ${p.version}</span>
                </div>
                <pre class="policy-rules">${JSON.stringify(p.rules, null, 2)}</pre>
            </div>
        `).join("");
    } catch (e) {
        listContainer.innerHTML = `<div class="loading-placeholder text-critical">Failed to load policies: ${e.message}</div>`;
    }
}

// Policy Action Elements
document.getElementById("new-policy-btn").addEventListener("click", () => showModal("modal-policy"));

document.getElementById("new-policy-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const policyId = document.getElementById("policy-id-input").value.trim();
    const rulesText = document.getElementById("policy-rules-input").value.trim();
    const statusDiv = document.getElementById("policy-create-status");
    
    try {
        const rules = JSON.parse(rulesText);
        await apiCall("/api/v1/policies", "POST", { policy_id: policyId, rules });
        statusDiv.textContent = "Policy rules registered successfully.";
        loadPoliciesWorkspace();
        setTimeout(() => {
            closeModal("modal-policy");
            statusDiv.textContent = "";
            document.getElementById("new-policy-form").reset();
        }, 1500);
    } catch (err) {
        statusDiv.textContent = `Registration error: ${err.message}`;
        statusDiv.className = "error-msg";
    }
});

// Dynamic form display for Policy target selectors
document.getElementById("assign-target-type").addEventListener("change", (e) => {
    const valContainer = document.getElementById("assign-target-val-container");
    if (e.target.value === "global") {
        valContainer.classList.add("display-none");
        document.getElementById("assign-target-val").required = false;
    } else {
        valContainer.classList.remove("display-none");
        document.getElementById("assign-target-val").required = true;
    }
});

document.getElementById("assign-policy-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const policyId = document.getElementById("assign-policy-id").value;
    const targetType = document.getElementById("assign-target-type").value;
    const targetVal = document.getElementById("assign-target-val").value.trim();
    const statusDiv = document.getElementById("assign-status");
    
    const body = { target_type: targetType };
    if (targetType === "group") body.group_id = targetVal;
    if (targetType === "device") body.device_id = targetVal;
    
    try {
        await apiCall(`/api/v1/policies/${policyId}/assign`, "POST", body);
        statusDiv.textContent = "Policy rules assignment configured successfully.";
        setTimeout(() => { statusDiv.textContent = ""; }, 3000);
    } catch (err) {
        statusDiv.textContent = `Assignment failed: ${err.message}`;
        statusDiv.className = "error-msg";
    }
});

// --- TAB: UPDATE CAMPAIGNS ---
async function loadUpdatesWorkspace() {
    const releasesContainer = document.getElementById("updates-releases-container");
    const campaignsContainer = document.getElementById("campaigns-grid-container");
    const releaseSelect = document.getElementById("campaign-release");
    
    releasesContainer.innerHTML = '<div class="loading-placeholder">Loading releases...</div>';
    campaignsContainer.innerHTML = '<div class="loading-placeholder">Loading campaigns...</div>';
    
    try {
        const releases = await apiCall("/api/v1/updates/releases");
        releaseSelect.innerHTML = '<option value="">Select Release...</option>' + 
            releases.map(r => `<option value="${r.version}">${r.version}</option>`).join("");
            
        releasesContainer.innerHTML = releases.map(r => `
            <div class="release-item-card">
                <div class="release-header">
                    <span class="release-title">📦 Version ${r.version}</span>
                    <span class="badge-role">${r.channel}</span>
                </div>
                <p class="release-desc">Filename: ${r.filename}<br>Hash: ${r.checksum_sha256}</p>
            </div>
        `).join("");
        
        const campaigns = await apiCall("/api/v1/updates/campaigns");
        if (campaigns.length === 0) {
            campaignsContainer.innerHTML = '<div class="loading-placeholder">No update campaigns found.</div>';
            return;
        }
        
        campaignsContainer.innerHTML = campaigns.map(camp => {
            const total = camp.total_devices || 1;
            const progress = Math.round((camp.completed_devices / total) * 100);
            return `
                <div class="campaign-card">
                    <div class="campaign-header">
                        <strong>${camp.campaign_id}</strong>
                        <span class="campaign-state-pill ${camp.status}">${camp.status}</span>
                    </div>
                    <div class="user-org">Target: ${camp.target_release_version} (${camp.target_channel})</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <div class="flex-row justify-between text-muted" style="font-size: 11px;">
                        <span>Progress: ${progress}%</span>
                        <span>${camp.completed_devices} / ${total} Nodes</span>
                    </div>
                    <div class="campaign-actions">
                        ${camp.status === 'running' ? `<button onclick="controlCampaign('${camp.campaign_id}', 'pause')" class="btn-secondary">Pause</button>` : ''}
                        ${camp.status === 'paused' ? `<button onclick="controlCampaign('${camp.campaign_id}', 'resume')" class="btn-primary-sm">Resume</button>` : ''}
                        ${camp.status !== 'completed' ? `<button onclick="controlCampaign('${camp.campaign_id}', 'rollback')" class="btn-secondary">Rollback</button>` : ''}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        releasesContainer.innerHTML = '<div class="loading-placeholder">Failed to load.</div>';
        campaignsContainer.innerHTML = `<div class="loading-placeholder">Failed to load campaigns: ${e.message}</div>`;
    }
}

document.getElementById("create-campaign-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("campaign-id").value.trim();
    const version = document.getElementById("campaign-release").value;
    const channel = document.getElementById("campaign-channel").value;
    const strategy = document.getElementById("campaign-stages").value;
    const statusDiv = document.getElementById("campaign-create-status");
    
    const body = {
        campaign_id: id,
        target_release_version: version,
        target_channel: channel,
        rollout_strategy: strategy
    };
    
    try {
        await apiCall("/api/v1/updates/campaigns", "POST", body);
        statusDiv.textContent = "Rollout campaign initiated successfully.";
        loadUpdatesWorkspace();
        setTimeout(() => {
            statusDiv.textContent = "";
            document.getElementById("create-campaign-form").reset();
        }, 2000);
    } catch (err) {
        statusDiv.textContent = `Initiation failed: ${err.message}`;
        statusDiv.className = "error-msg";
    }
});

async function controlCampaign(id, action) {
    try {
        await apiCall(`/api/v1/updates/campaigns/${id}/${action}`, "POST");
        loadUpdatesWorkspace();
    } catch (e) {
        alert(`Action failed: ${e.message}`);
    }
}

// --- TAB: GOVERNANCE & COMPLIANCE ---
document.getElementById("verify-audit-btn").addEventListener("click", async () => {
    const card = document.getElementById("verify-audit-result");
    const indicator = document.getElementById("verify-status-indicator");
    const statusText = document.getElementById("verify-status-text");
    const statusMsg = document.getElementById("verify-status-msg");
    const statusRaw = document.getElementById("verify-status-raw");
    
    card.classList.remove("display-none");
    card.className = "verify-result-card";
    statusText.textContent = "Status: Executing scanning crawler...";
    indicator.className = "pulse-green";
    statusMsg.textContent = "";
    statusRaw.textContent = "";
    
    try {
        const verifyRes = await apiCall("/api/v1/audit/verify", "POST");
        statusRaw.textContent = JSON.stringify(verifyRes, null, 2);
        
        if (verifyRes.status === "valid") {
            card.classList.add("valid");
            statusText.textContent = "Status: Cryptographic Chain Verified";
            indicator.className = "pulse-green";
            statusMsg.textContent = `All ${verifyRes.scanned_records} audit entries parsed successfully. The cryptographic SHA256 chain is valid and untampered.`;
        } else {
            card.classList.add("tampered");
            statusText.textContent = "Status: Cryptographic Chain Broken";
            indicator.className = "pulse-red";
            statusMsg.textContent = `Tampering detected at row event '${verifyRes.broken_event_id}'. Calculated signature does not match stored block target.`;
        }
    } catch (e) {
        statusText.textContent = "Verification Failed";
        statusMsg.textContent = e.message;
    }
});

async function triggerEvidenceExport(reportType) {
    const viewer = document.getElementById("export-viewer");
    const statusDiv = document.getElementById("export-status");
    
    viewer.classList.add("display-none");
    statusDiv.textContent = `Generating '${reportType}' compliance evidence package...`;
    
    try {
        const records = await apiCall(`/api/v1/compliance/export/${reportType}`);
        statusDiv.textContent = `Successfully exported ${records.length} records in evidence format.`;
        viewer.textContent = JSON.stringify(records, null, 2);
        viewer.classList.remove("display-none");
    } catch (e) {
        statusDiv.textContent = `Export failed: ${e.message}`;
    }
}

// --- TAB: DIAGNOSTICS & INCIDENTS ---
async function loadDiagnosticsWorkspace() {
    const incidentContainer = document.getElementById("incidents-list-container");
    const bundlesTbody = document.getElementById("support-bundles-table-body");
    const diagDeviceSelect = document.getElementById("diag-target-device");
    const incDeviceSelect = document.getElementById("incident-device-input");
    
    incidentContainer.innerHTML = '<div class="loading-placeholder">Loading incidents...</div>';
    bundlesTbody.innerHTML = '<tr><td colspan="7" class="text-center">Loading support packages...</td></tr>';
    
    try {
        // Load active reporting device selectors
        const devices = await apiCall("/api/v1/devices");
        const options = '<option value="">Select Device...</option>' + 
            devices.map(d => `<option value="${d.device_id}">${d.device_id} (${d.device_model})</option>`).join("");
            
        diagDeviceSelect.innerHTML = options;
        incDeviceSelect.innerHTML = options;
        
        // Load incidents tickets CRM
        const incidents = await apiCall("/api/v1/support/incidents");
        if (incidents.length === 0) {
            incidentContainer.innerHTML = '<div class="loading-placeholder">No active tickets. All systems nominal.</div>';
        } else {
            incidentContainer.innerHTML = incidents.map(inc => `
                <div class="incident-card ${inc.severity}">
                    <div class="policy-header">
                        <strong>${inc.title}</strong>
                        <span class="badge-role">${inc.severity.toUpperCase()}</span>
                    </div>
                    <div class="incident-body">
                        Device: ${inc.device_id}<br>
                        Status: <span class="badge-state ${inc.status}">${inc.status}</span><br>
                        Description: ${inc.description || "No detail provided"}
                    </div>
                    <div class="notes-container">
                        ${(inc.operator_notes || []).map(n => `
                            <div class="note-row">
                                [${formatTimestamp(n.timestamp)}] ${n.note}
                            </div>
                        `).join("")}
                        <div class="incident-input-row">
                            <input type="text" id="note-input-${inc.incident_id}" placeholder="Add operator note...">
                            <button onclick="addIncidentNote('${inc.incident_id}')" class="btn-primary-sm">Add</button>
                            <button onclick="resolveIncident('${inc.incident_id}')" class="btn-secondary">Resolve</button>
                        </div>
                    </div>
                </div>
            `).join("");
        }
        
        // Load support bundle registry listings
        const bundles = await apiCall("/api/v1/support/bundles");
        if (bundles.length === 0) {
            bundlesTbody.innerHTML = '<tr><td colspan="7" class="text-center">No diagnostic support bundles uploaded.</td></tr>';
            return;
        }
        
        bundlesTbody.innerHTML = bundles.map(b => `
            <tr>
                <td><small class="font-mono">${b.bundle_id}</small></td>
                <td><strong>${b.device_id}</strong></td>
                <td>${formatTimestamp(b.timestamp)}</td>
                <td>${b.bundle_size_bytes}</td>
                <td>${b.trigger_reason}</td>
                <td>${b.redaction_applied ? "✅ Yes" : "❌ No"}</td>
                <td><a href="${b.bundle_url}" target="_blank" class="btn-action">Download Package</a></td>
            </tr>
        `).join("");
    } catch (e) {
        incidentContainer.innerHTML = '<div class="loading-placeholder">Failed to load incidents.</div>';
        bundlesTbody.innerHTML = `<tr><td colspan="7" class="text-center text-critical">Failed to load support bundles: ${e.message}</td></tr>`;
    }
}

// Add note to support incident
async function addIncidentNote(incidentId) {
    const input = document.getElementById(`note-input-${incidentId}`);
    const note = input.value.trim();
    if (!note) return;
    
    try {
        await apiCall(`/api/v1/support/incidents/${incidentId}`, "PATCH", { operator_note: note });
        loadDiagnosticsWorkspace();
    } catch (e) {
        alert(e.message);
    }
}

// Resolve support incident
async function resolveIncident(incidentId) {
    try {
        await apiCall(`/api/v1/support/incidents/${incidentId}`, "PATCH", { status: "resolved", operator_note: "Incident ticket marked resolved by operator." });
        loadDiagnosticsWorkspace();
    } catch (e) {
        alert(e.message);
    }
}

// Remote Diagnostics Command Console dispatcher
document.getElementById("diag-target-device").addEventListener("change", (e) => {
    const deviceId = e.target.value;
    if (deviceId) {
        loadDeviceTimelineDetails(deviceId);
    }
});

async function loadDeviceTimelineDetails(deviceId) {
    const term = document.getElementById("terminal-stdout");
    term.innerHTML = `Connecting to client remote execution agent on node '${deviceId}'...<br>`;
    
    try {
        const timeline = await apiCall(`/api/v1/devices/${deviceId}/timeline`);
        term.innerHTML += `Connected successfully. Fetched device timeline:<br><br>`;
        term.innerHTML += timeline.map(event => `
            [${formatTimestamp(event.timestamp)}] <span class="text-warning">${event.event_type.toUpperCase()}</span>: ${event.title}
        `).join("<br>");
    } catch (e) {
        term.innerHTML += `<span class="text-red">Error querying node timeline: ${e.message}</span>`;
    }
}

document.getElementById("terminal-execute-btn").addEventListener("click", async () => {
    const deviceId = document.getElementById("diag-target-device").value;
    const command = document.getElementById("terminal-command-select").value;
    const term = document.getElementById("terminal-stdout");
    
    if (!deviceId) {
        alert("Please select a target device.");
        return;
    }
    if (!command) {
        alert("Please select an execution command.");
        return;
    }
    
    term.innerHTML += `<br><br>$ ${command}<br>Scheduling task execution...`;
    
    // Generate UUID task id
    const commandId = "cmd_exec_" + Math.random().toString(36).substring(2, 10);
    
    try {
        // Enqueue diagnostic execute command
        await apiCall(`/api/v1/devices/${deviceId}/diagnostics/execute`, "POST", {
            command_id: commandId,
            command
        });
        
        term.innerHTML += `<br>Task enqueued. Status: PENDING. Waiting for device plane polling...`;
        
        // Start simulated device plane poll execute loops in backend
        setTimeout(() => {
            simulateDeviceAgentPollExecute(deviceId, commandId);
        }, 1500);
        
    } catch (e) {
        term.innerHTML += `<br><span class="text-red">Scheduling failed: ${e.message}</span>`;
    }
});

// Mock simulation of device polling and execution results reporting
async function simulateDeviceAgentPollExecute(deviceId, commandId) {
    const term = document.getElementById("terminal-stdout");
    
    try {
        // 1. Device polls pending command promoting state to RUNNING
        const cmd = await apiCall(`/api/v1/devices/${deviceId}/diagnostics/pending`);
        if (cmd && cmd.command_id === commandId) {
            term.innerHTML += `<br>Device pulled task. Status: RUNNING. Executing binary packages shell...`;
            
            // 2. Device reports results after a brief delay
            setTimeout(async () => {
                let mockOutput = "cerynix-base.service is running";
                if (cmd.command === "reboot") {
                    mockOutput = "Reboot command received. System is going down for reboot now!";
                } else if (cmd.command.startsWith("journalctl")) {
                    mockOutput = "-- Logs begin at Tue 2026-06-30 --\nJun 30 15:00:00 cerynix systemd[1]: Starting base daemon...\nJun 30 15:00:02 cerynix cerynix-base[123]: Initialized successfully.";
                } else if (cmd.command.includes("cerynix-diag")) {
                    mockOutput = "Cerynix Diagnostics v1.0.0\n[OK] Kernel Integrity checked\n[OK] SHA256 Chained verify matches genesis block.";
                }
                
                await apiCall(`/api/v1/devices/${deviceId}/diagnostics/results`, "POST", {
                    command_id: commandId,
                    status: "completed",
                    output: mockOutput
                });
                
                term.innerHTML += `<br>Task execution completed successfully.<br><pre class="raw-code" style="color: #4AF626; border: none; background: transparent; padding: 0;">${mockOutput}</pre>`;
                term.scrollTop = term.scrollHeight;
            }, 2000);
        }
    } catch (e) {
        term.innerHTML += `<br><span class="text-red">Device agent execution loop failed: ${e.message}</span>`;
    }
}

// Open tickets modal
document.getElementById("new-incident-btn").addEventListener("click", () => showModal("modal-incident"));

document.getElementById("new-incident-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("incident-id-input").value.trim();
    const deviceId = document.getElementById("incident-device-input").value;
    const title = document.getElementById("incident-title-input").value.trim();
    const desc = document.getElementById("incident-desc-input").value.trim();
    const severity = document.getElementById("incident-severity-input").value;
    
    try {
        await apiCall("/api/v1/support/incidents", "POST", {
            incident_id: id,
            device_id: deviceId,
            title,
            description: desc,
            severity
        });
        loadDiagnosticsWorkspace();
        closeModal("modal-incident");
        document.getElementById("new-incident-form").reset();
    } catch (err) {
        alert(`Incident log failed: ${err.message}`);
    }
});

// --- TAB: SIMULATORS ---
async function loadSimulatorsWorkspace() {
    const simDeviceSelect = document.getElementById("sim-device-id");
    
    try {
        const devices = await apiCall("/api/v1/devices");
        simDeviceSelect.innerHTML = '<option value="">Select Device to Fail...</option>' + 
            devices.map(d => `<option value="${d.device_id}">${d.device_id} (${d.device_model})</option>`).join("");
    } catch (e) {
        console.error("Failed to load device selectors inside failure simulator workspace", e);
    }
}

document.getElementById("simulate-failure-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const deviceId = document.getElementById("sim-device-id").value;
    const failureType = document.getElementById("sim-failure-type").value;
    const statusDiv = document.getElementById("sim-status");
    
    statusDiv.textContent = "Injecting failure signature...";
    
    try {
        const result = await apiCall(`/api/v1/devices/${deviceId}/simulate-failure`, "POST", { failure_type: failureType });
        statusDiv.textContent = `Successfully injected '${failureType}' error state. Latest health score: ${result.health_score}.`;
        
        // Trigger alerts check refresh in 1s
        setTimeout(() => {
            loadOverviewMetrics();
        }, 1000);
        
        setTimeout(() => { statusDiv.textContent = ""; }, 4000);
    } catch (err) {
        statusDiv.textContent = `Injection failed: ${err.message}`;
        statusDiv.className = "error-msg";
    }
});

// Global alerts polling hooks
function startAlertsPolling() {
    loadOverviewMetrics();
    alertPollInterval = setInterval(loadOverviewMetrics, 10000); // Poll alerts every 10s
}

function stopAlertsPolling() {
    if (alertPollInterval) {
        clearInterval(alertPollInterval);
        alertPollInterval = null;
    }
}

// Global modal windows controls
function showModal(modalId) {
    document.getElementById(modalId).classList.remove("display-none");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add("display-none");
}

// Utility: format timestamp strings
function formatTimestamp(tsStr) {
    if (!tsStr) return "";
    try {
        const dt = new Date(tsStr);
        return dt.toLocaleTimeString() + " " + dt.toLocaleDateString();
    } catch {
        return tsStr;
    }
}

// Initialise Token on load
window.addEventListener("DOMContentLoaded", () => {
    if (authToken) {
        authModal.classList.add("display-none");
        consoleLayout.classList.remove("layout-hidden");
        startAlertsPolling();
        switchTab(activeTab);
    } else {
        authModal.classList.remove("display-none");
    }
});
