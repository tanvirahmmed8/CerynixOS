def prompt_recovery(scenario: str, action_command: str) -> bool:
    print("\n" + "="*50)
    print(f"⚠️  CERYNIXOS RECOVERY ADVISOR: {scenario.upper()}")
    print("="*50)
    print(f"Detected issue: {scenario}")
    print(f"Recommended action: `{action_command}`")
    print("-" * 50)
    
    while True:
        choice = input("Do you want to proceed with this recovery action? [y/N]: ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no', '']:
            return False
        print("Please answer 'y' or 'n'.")

if __name__ == "__main__":
    # Test execution
    approved = prompt_recovery("Storage Pressure (>90% full)", "nix-collect-garbage -d")
    print(f"User approved: {approved}")
