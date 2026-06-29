import json
import os
from datetime import datetime

class TaskMemory:
    def __init__(self, db_path="/var/lib/cerynixos-ai/memory.json", max_retention=100):
        self.db_path = db_path
        self.max_retention = max_retention
        self.privacy_mode = False
        self._memory = []
        self._load()

    def set_privacy_mode(self, enabled: bool):
        self.privacy_mode = enabled
        if enabled:
            self.clear()

    def _load(self):
        if os.path.exists(self.db_path) and not self.privacy_mode:
            try:
                with open(self.db_path, "r") as f:
                    self._memory = json.load(f)
            except:
                self._memory = []

    def _save(self):
        if self.privacy_mode: return
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self._memory[-self.max_retention:], f)

    def add_event(self, role: str, content: str):
        if self.privacy_mode: return
        self._memory.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "content": content
        })
        self._save()

    def get_context(self, limit=10):
        return self._memory[-limit:]

    def clear(self):
        self._memory = []
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
