import sqlite3
from database.connection import get_db_connection

TABLES = {
    "device_groups": """
        CREATE TABLE IF NOT EXISTS device_groups (
            group_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            release_channel TEXT CHECK(release_channel IN ('canary', 'pilot', 'broad', 'critical')) DEFAULT 'broad',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "enrollment_tokens": """
        CREATE TABLE IF NOT EXISTS enrollment_tokens (
            token TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            max_uses INTEGER DEFAULT 1,
            uses INTEGER DEFAULT 0
        );
    """,
    "devices": """
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            device_model TEXT NOT NULL,
            os_version TEXT NOT NULL,
            cpu_cores INTEGER NOT NULL,
            memory_bytes INTEGER NOT NULL,
            storage_bytes INTEGER NOT NULL,
            installed_capabilities TEXT,
            enrollment_state TEXT CHECK(enrollment_state IN ('enrolled', 'active', 'quarantined', 'retired')) DEFAULT 'enrolled',
            tags TEXT,
            group_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES device_groups(group_id) ON DELETE SET NULL
        );
    """,
    "policies": """
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            version INTEGER NOT NULL,
            rules TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "policy_assignments": """
        CREATE TABLE IF NOT EXISTS policy_assignments (
            assignment_id TEXT PRIMARY KEY,
            policy_id TEXT NOT NULL,
            target_type TEXT CHECK(target_type IN ('global', 'group', 'device')) NOT NULL,
            target_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id) ON DELETE CASCADE
        );
    """,
    "releases": """
        CREATE TABLE IF NOT EXISTS releases (
            release_id TEXT PRIMARY KEY,
            version TEXT UNIQUE NOT NULL,
            channel TEXT CHECK(channel IN ('canary', 'pilot', 'broad', 'critical')) NOT NULL,
            image_url TEXT NOT NULL,
            sha256_hash TEXT NOT NULL,
            force_rollback INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "campaigns": """
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id TEXT PRIMARY KEY,
            release_id TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT CHECK(status IN ('active', 'paused', 'completed', 'rolled_back')) DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(release_id) REFERENCES releases(release_id) ON DELETE CASCADE
        );
    """,
    "campaign_targets": """
        CREATE TABLE IF NOT EXISTS campaign_targets (
            campaign_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'downloading', 'applying', 'verified', 'failed')) DEFAULT 'pending',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(campaign_id, device_id),
            FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "audit_events": """
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            service TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            previous_hash TEXT,
            tamper_hash TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "health_snapshots": """
        CREATE TABLE IF NOT EXISTS health_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            health_score INTEGER NOT NULL,
            cpu TEXT CHECK(cpu IN ('healthy', 'degraded', 'critical')) NOT NULL,
            memory TEXT CHECK(memory IN ('healthy', 'degraded', 'critical')) NOT NULL,
            storage TEXT CHECK(storage IN ('healthy', 'degraded', 'critical')) NOT NULL,
            services TEXT CHECK(services IN ('healthy', 'degraded', 'critical')) NOT NULL,
            metrics TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "support_bundles": """
        CREATE TABLE IF NOT EXISTS support_bundles (
            bundle_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            bundle_size_bytes INTEGER NOT NULL,
            bundle_url TEXT NOT NULL,
            trigger_reason TEXT NOT NULL,
            redaction_applied INTEGER DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "policy_revisions": """
        CREATE TABLE IF NOT EXISTS policy_revisions (
            revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            rules TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id) ON DELETE CASCADE,
            UNIQUE(policy_id, version)
        );
    """,
    "incidents": """
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT CHECK(status IN ('open', 'resolved', 'investigating')) DEFAULT 'open',
            severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
            operator_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "diagnostic_commands": """
        CREATE TABLE IF NOT EXISTS diagnostic_commands (
            command_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            command TEXT NOT NULL,
            arguments TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed')) DEFAULT 'pending',
            output TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
        );
    """,
    "registry_artifacts": """
        CREATE TABLE IF NOT EXISTS registry_artifacts (
            artifact_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('system', 'model', 'plugin')) NOT NULL,
            version TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            checksum_sha256 TEXT NOT NULL,
            download_url TEXT NOT NULL,
            signature TEXT NOT NULL,
            approval_status TEXT CHECK(approval_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(type, name, version)
        );
    """
}

def init_db():
    """Initializes the SQLite database schemas and creates tables if they do not exist."""
    print("Initializing SQLite database schemas...")
    with get_db_connection() as conn:
        # Create tables in order of dependencies (independent first)
        ordered_tables = [
            "device_groups",
            "enrollment_tokens",
            "devices",
            "policies",
            "policy_assignments",
            "policy_revisions",
            "releases",
            "campaigns",
            "campaign_targets",
            "audit_events",
            "health_snapshots",
            "support_bundles",
            "incidents",
            "diagnostic_commands",
            "registry_artifacts"
        ]
        for name in ordered_tables:
            conn.execute(TABLES[name])
            
        # Run migration check for release_channel in device_groups
        try:
            conn.execute("ALTER TABLE device_groups ADD COLUMN release_channel TEXT CHECK(release_channel IN ('canary', 'pilot', 'broad', 'critical')) DEFAULT 'broad';")
        except sqlite3.OperationalError:
            # Column already exists
            pass
            
        # Run migration check for previous_hash and tamper_hash in audit_events
        try:
            conn.execute("ALTER TABLE audit_events ADD COLUMN previous_hash TEXT;")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE audit_events ADD COLUMN tamper_hash TEXT;")
        except sqlite3.OperationalError:
            pass
            
    print("Database initialization completed successfully.")
