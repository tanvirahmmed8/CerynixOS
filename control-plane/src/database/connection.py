import sqlite3
import os
import json
from contextlib import contextmanager

def get_workspace_root():
    # connection.py is in control-plane/src/database/
    # Workspace root is 3 levels up
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

def load_config():
    root = get_workspace_root()
    config_path = os.path.join(root, "control-plane/config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            try:
                return json.load(f)
            except Exception:
                pass
    # Fallback defaults
    return {
        "host": "127.0.0.1",
        "port": 8000,
        "db_path": "control-plane/db/control_plane.db",
        "api_token": "token_cerynix_secret_key_2026",
        "log_level": "INFO"
    }

def get_db_path():
    config = load_config()
    db_path = config.get("db_path", "control-plane/db/control_plane.db")
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(get_workspace_root(), db_path))
    return db_path

@contextmanager
def get_db_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Enable WAL mode for concurrency and Foreign Keys for integrity
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
