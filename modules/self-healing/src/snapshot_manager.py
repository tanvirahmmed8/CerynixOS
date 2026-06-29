import os
import shutil
import time

CONFIG_DIR = os.path.expanduser("~/.config/cerynixos")
BACKUP_DIR = os.path.expanduser("~/.local/share/cerynixos/backups")

def create_snapshot():
    if not os.path.exists(CONFIG_DIR):
        print("No user config directory found to snapshot.")
        return
        
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = str(int(time.time()))
    dest = os.path.join(BACKUP_DIR, f"config_snapshot_{timestamp}")
    
    shutil.copytree(CONFIG_DIR, dest)
    print(f"Created config snapshot at {dest}")

def restore_latest_snapshot():
    if not os.path.exists(BACKUP_DIR):
        print("No backups available.")
        return False
        
    backups = sorted(os.listdir(BACKUP_DIR))
    if not backups:
        print("No backups available.")
        return False
        
    latest = os.path.join(BACKUP_DIR, backups[-1])
    
    if os.path.exists(CONFIG_DIR):
        shutil.rmtree(CONFIG_DIR)
        
    shutil.copytree(latest, CONFIG_DIR)
    print(f"Restored user config from {latest}")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_latest_snapshot()
    else:
        create_snapshot()
