import json
import os
 
# ── File where data is saved ──────────────────────────────────────────────────
DATA_FILE = "data_usage.json"
 
 
# ── File helpers ──────────────────────────────────────────────────────────────
 
def load_data():
    """Load saved data from file. Returns (usage_dict, daily_limit)."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
            usage = saved.get("usage", {})
            limit = saved.get("daily_limit", 0)
            print("✔  Previous data loaded successfully.\n")
            return usage, limit
        except (json.JSONDecodeError, KeyError):
            print("⚠  Could not read saved data. Starting fresh.\n")
    return {}, 0
 
 
def save_data(usage, daily_limit):
    """Save current data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump({"usage": usage, "daily_limit": daily_limit}, f, indent=4)
    print("✔  Data saved successfully.")
 
 
# ── Core features ─────────────────────────────────────────────────────────────
 
def add_usage(usage):
    """Ask the user for an app name and data used, then record it."""
    print("\n--- Add Data Usage ---")
 
    app_name = input("Enter app name (e.g. YouTube, Instagram): ").strip()
    if not app_name:
        print("⚠  App name cannot be empty.")
        return
 
    # Normalise to title-case so 'youtube' and 'YouTube' merge together
    app_name = app_name.title()
 
    try:
        amount = float(input(f"Enter data used by {app_name} (in MB): ").strip())
        if amount < 0:
            print("⚠  Data usage cannot be negative.")
            return
    except ValueError:
        print("⚠  Please enter a valid number.")
        return
 
    # Add to existing value or create new entry
    if app_name in usage:
        usage[app_name] += amount
    else:
        usage[app_name] = amount
 
    print(f"✔  Added {amount:.2f} MB for {app_name}.")
 
 
def set_daily_limit():
    """Ask the user to enter a daily data limit in MB."""
    print("\n--- Set Daily Data Limit ---")
    try:
        limit = float(input("Enter your daily data limit (in MB): ").strip())
        if limit < 0:
            print("⚠  Limit cannot be negative.")
            return 0
        print(f"✔  Daily limit set to {limit:.2f} MB.")
        return limit
    except ValueError:
        print("⚠  Please enter a valid number.")
        return 0
 
 
def calculate_total(usage):
    """Return the sum of all app usages."""
    return sum(usage.values())
 
 
def get_highest_usage(usage):
    """Return the app name and MB value with the highest usage."""
    if not usage:
        return None, 0
    top_app = max(usage, key=usage.get)
    return top_app, usage[top_app]
 
 
def display_summary(usage, daily_limit):
    """Print a nicely formatted summary of all usage."""
    print("\n" + "=" * 40)
    print("       MOBILE DATA USAGE SUMMARY")
    print("=" * 40)
 
    if not usage:
        print("  No data recorded yet.")
        print("=" * 40)
        return
 
    # Per-app breakdown
    print(f"  {'App':<20} {'Usage (MB)':>10}")
    print("  " + "-" * 32)
    for app, mb in sorted(usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {app:<20} {mb:>10.2f}")
 
    print("  " + "-" * 32)
 
    total = calculate_total(usage)
    print(f"  {'TOTAL':<20} {total:>10.2f} MB")
 
    # Highest usage app
    top_app, top_mb = get_highest_usage(usage)
    print(f"\n  Highest usage : {top_app} ({top_mb:.2f} MB)")
 
    # Daily limit check
    if daily_limit > 0:
        remaining = daily_limit - total
        print(f"  Daily limit   : {daily_limit:.2f} MB")
        if remaining >= 0:
            print(f"  Remaining     : {remaining:.2f} MB")
        else:
            print(f"\n  ⚠  WARNING: You have exceeded your daily limit by "
                  f"{abs(remaining):.2f} MB!")
    else:
        print("  Daily limit   : Not set")
 
    print("=" * 40)
 
 
def reset_data(usage):
    """Clear all usage data after confirmation."""
    confirm = input("\nAre you sure you want to reset all data? (yes/no): ").strip().lower()
    if confirm == "yes":
        usage.clear()
        print("✔  All data has been reset.")
    else:
        print("  Reset cancelled.")
 
 
# ── Menu ──────────────────────────────────────────────────────────────────────
 
def print_menu():
    print("\n╔══════════════════════════════╗")
    print("║   MOBILE DATA USAGE TRACKER  ║")
    print("╠══════════════════════════════╣")
    print("║  1. Add data usage           ║")
    print("║  2. View summary             ║")
    print("║  3. Set daily data limit     ║")
    print("║  4. Reset all data           ║")
    print("║  5. Save and exit            ║")
    print("╚══════════════════════════════╝")
    print("Enter your choice (1-5): ", end="")
 
 
# ── Main program ──────────────────────────────────────────────────────────────
 
def main():
    # Load any previously saved data
    usage, daily_limit = load_data()
 
    while True:
        print_menu()
        choice = input().strip()
 
        if choice == "1":
            add_usage(usage)
 
        elif choice == "2":
            display_summary(usage, daily_limit)
 
        elif choice == "3":
            new_limit = set_daily_limit()
            if new_limit > 0:
                daily_limit = new_limit
 
        elif choice == "4":
            reset_data(usage)
 
        elif choice == "5":
            save_data(usage, daily_limit)
            print("Goodbye! 👋")
            break
 
        else:
            print("⚠  Invalid choice. Please enter a number from 1 to 5.")
 
 
# Entry point
if __name__ == "__main__":
    main()
 
