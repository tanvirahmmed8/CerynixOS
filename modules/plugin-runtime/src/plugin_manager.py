#!/usr/bin/env python3
import sys
import os
import shutil
import json

PLUGIN_DIR = "/var/lib/cerynixos-plugins"

def install(src_path: str):
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found.")
        sys.exit(1)
        
    manifest_path = os.path.join(src_path, "manifest.json")
    if not os.path.exists(manifest_path):
        print("Error: Invalid plugin, no manifest.json found.")
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    name = manifest.get("name")
    if not name:
        print("Error: Plugin manifest missing 'name'.")
        sys.exit(1)
        
    dest = os.path.join(PLUGIN_DIR, name)
    if os.path.exists(dest):
        print(f"Error: Plugin {name} is already installed. Use remove first.")
        sys.exit(1)
        
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    shutil.copytree(src_path, dest)
    print(f"Successfully installed plugin: {name}")

def remove(name: str):
    dest = os.path.join(PLUGIN_DIR, name)
    if not os.path.exists(dest):
        print(f"Error: Plugin {name} not found.")
        sys.exit(1)
    shutil.rmtree(dest)
    print(f"Successfully removed plugin: {name}")

def list_plugins():
    if not os.path.exists(PLUGIN_DIR):
        print("No plugins installed.")
        return
        
    plugins = os.listdir(PLUGIN_DIR)
    if not plugins:
        print("No plugins installed.")
        return
        
    print("Installed Plugins:")
    print("-" * 40)
    for p in plugins:
        manifest_path = os.path.join(PLUGIN_DIR, p, "manifest.json")
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            print(f"- {manifest.get('name')} v{manifest.get('version')}: {manifest.get('description')}")
        except:
            print(f"- {p} (Broken manifest)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cerynix-plugin-manager [install <path> | remove <name> | list]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "install" and len(sys.argv) == 3:
        install(sys.argv[2])
    elif cmd == "remove" and len(sys.argv) == 3:
        remove(sys.argv[2])
    elif cmd == "list":
        list_plugins()
    else:
        print("Invalid command arguments.")
        sys.exit(1)
