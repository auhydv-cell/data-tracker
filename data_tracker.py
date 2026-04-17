Internet & Mobile Data Usage Tracker
=====================================
Tracks REAL-TIME internet data (upload/download) on your computer using psutil,
PLUS lets you manually log per-app usage — all in one program.

Requirements:
    pip install psutil
"""

import json
import os
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE   = "data_usage.json"
BYTES_IN_MB = 1024 * 1024
BYTES_IN_GB = 1024 * 1024 * 1024


# ── Helper: clear the terminal (works on Windows, Mac, Linux) ─────────────────
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ── Helper: format bytes into readable MB / GB ────────────────────────────────
def format_bytes(byte_count):
    """Convert a raw byte count into a human-readable MB or GB string."""
    if byte_count >= BYTES_IN_GB:
        return f"{byte_count / BYTES_IN_GB:.3f} GB"
    return f"{byte_count / BYTES_IN_MB:.2f} MB"


# ── Helper: simple progress bar ───────────────────────────────────────────────
def progress_bar(used, total, width=30):
    """Return a text progress bar, e.g.  [████████░░░░░░]  55%"""
    if total <= 0:
        return ""
    ratio  = min(used / total, 1.0)
    filled = int(width * ratio)
    bar    = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {ratio * 100:.1f}%"


# ── File helpers ──────────────────────────────────────────────────────────────
def load_data():
    """Load saved app-usage data and daily limit from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
            usage = saved.get("usage", {})
            limit = saved.get("daily_limit", 0)
            print("Previous data loaded successfully.\n")
            return usage, limit
        except (json.JSONDecodeError, KeyError):
            print("Could not read saved data. Starting fresh.\n")
    return {}, 0


def save_data(usage, daily_limit):
    """Save app-usage data and daily limit to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump({"usage": usage, "daily_limit": daily_limit}, f, indent=4)
    print("Data saved successfully.")


# ── Real-time monitor ─────────────────────────────────────────────────────────
def monitor_realtime(daily_limit_mb):
    """
    Use psutil to monitor live upload & download speed.
    Clears the screen each second for a clean, flicker-free refresh.
    Works on Windows CMD, PowerShell, macOS Terminal, and Linux.
    Press Ctrl+C to stop. Returns total session data in MB.
    """
    if not PSUTIL_AVAILABLE:
        print("\npsutil is not installed.")
        print("   Run:  pip install psutil   then restart the program.")
        input("\nPress Enter to return to menu...")
        return 0

    # Snapshot counters at session start
    start_stats = psutil.net_io_counters()
    start_sent  = start_stats.bytes_sent
    start_recv  = start_stats.bytes_recv

    prev_sent = start_sent
    prev_recv = start_recv

    session_limit_bytes = daily_limit_mb * BYTES_IN_MB if daily_limit_mb > 0 else 0

    # Initialise totals so KeyboardInterrupt handler always has values
    total_sent    = 0
    total_recv    = 0
    total_session = 0

    try:
        while True:
            time.sleep(1)

            current    = psutil.net_io_counters()
            curr_sent  = current.bytes_sent
            curr_recv  = current.bytes_recv

            # Per-second speed
            speed_up   = curr_sent - prev_sent
            speed_down = curr_recv - prev_recv

            # Cumulative totals since monitoring started
            total_sent    = curr_sent - start_sent
            total_recv    = curr_recv - start_recv
            total_session = total_sent + total_recv

            # ── Redraw screen cleanly every second ───────────────────────
            clear_screen()
            print("=" * 50)
            print("   REAL-TIME INTERNET MONITOR  (Ctrl+C to stop)")
            print("=" * 50)
            print()
            print(f"  {'Upload speed':<18}: {format_bytes(speed_up)}/s")
            print(f"  {'Download speed':<18}: {format_bytes(speed_down)}/s")
            print()
            print(f"  {'Total uploaded':<18}: {format_bytes(total_sent)}")
            print(f"  {'Total downloaded':<18}: {format_bytes(total_recv)}")
            print(f"  {'Session total':<18}: {format_bytes(total_session)}")
            print()

            # Limit section
            if session_limit_bytes > 0:
                bar = progress_bar(total_session, session_limit_bytes)
                print(f"  Limit  {format_bytes(session_limit_bytes)}   {bar}")
                if total_session >= session_limit_bytes:
                    over = total_session - session_limit_bytes
                    print(f"\n  *** WARNING: Limit exceeded by {format_bytes(over)}! ***")
                else:
                    remaining = session_limit_bytes - total_session
                    print(f"  Remaining : {format_bytes(remaining)}")
            else:
                print("  Daily limit : Not set  (use option 4 to set one)")

            print()
            print("-" * 50)

            prev_sent = curr_sent
            prev_recv = curr_recv

    except KeyboardInterrupt:
        clear_screen()
        print("=" * 50)
        print("   SESSION SUMMARY")
        print("=" * 50)
        print(f"  Uploaded   : {format_bytes(total_sent)}")
        print(f"  Downloaded : {format_bytes(total_recv)}")
        print(f"  Total      : {format_bytes(total_session)}")
        print("=" * 50)
        return total_session / BYTES_IN_MB

    return 0


# ── Manual app-usage features ─────────────────────────────────────────────────
def add_usage(usage):
    """Manually log data usage for a named app."""
    print("\n--- Add App Data Usage ---")
    app_name = input("Enter app name (e.g. YouTube, Instagram): ").strip()
    if not app_name:
        print("App name cannot be empty.")
        return
    app_name = app_name.title()

    try:
        amount = float(input(f"Enter data used by {app_name} (in MB): ").strip())
        if amount < 0:
            print("Data usage cannot be negative.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    usage[app_name] = usage.get(app_name, 0) + amount
    print(f"Added {amount:.2f} MB for {app_name}.")


def set_daily_limit():
    """Prompt user to enter a daily data limit in MB."""
    print("\n--- Set Daily Data Limit ---")
    try:
        limit = float(input("Enter your daily data limit (in MB): ").strip())
        if limit < 0:
            print("Limit cannot be negative.")
            return 0
        print(f"Daily limit set to {limit:.2f} MB.")
        return limit
    except ValueError:
        print("Please enter a valid number.")
        return 0


def get_highest_usage(usage):
    """Return the (app_name, mb) pair with the highest recorded usage."""
    if not usage:
        return None, 0
    top_app = max(usage, key=usage.get)
    return top_app, usage[top_app]


def display_summary(usage, daily_limit):
    """Print a formatted table of all manually logged app usage."""
    print("\n" + "=" * 44)
    print("        APP DATA USAGE SUMMARY")
    print("=" * 44)

    if not usage:
        print("  No app data recorded yet.")
        print("=" * 44)
        return

    print(f"  {'App':<22} {'Usage (MB)':>10}")
    print("  " + "-" * 34)
    for app, mb in sorted(usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {app:<22} {mb:>10.2f}")

    print("  " + "-" * 34)
    total = sum(usage.values())
    print(f"  {'TOTAL':<22} {total:>10.2f} MB")

    top_app, top_mb = get_highest_usage(usage)
    print(f"\n  Highest usage  : {top_app} ({top_mb:.2f} MB)")

    if daily_limit > 0:
        remaining = daily_limit - total
        print(f"  Daily limit    : {daily_limit:.2f} MB")
        if remaining >= 0:
            print(f"  Remaining      : {remaining:.2f} MB")
        else:
            print(f"\n  WARNING: Exceeded daily limit by {abs(remaining):.2f} MB!")
    else:
        print("  Daily limit    : Not set")

    print("=" * 44)


def reset_data(usage):
    """Clear all manually logged usage after confirmation."""
    confirm = input("\nReset all app data? (yes/no): ").strip().lower()
    if confirm == "yes":
        usage.clear()
        print("All app data has been reset.")
    else:
        print("Reset cancelled.")


# ── Menu ──────────────────────────────────────────────────────────────────────
def print_menu():
    print("\n╔════════════════════════════════════╗")
    print("║   INTERNET & DATA USAGE TRACKER    ║")
    print("╠════════════════════════════════════╣")
    print("║  1. Monitor real-time internet     ║")
    print("║  2. Add app usage manually         ║")
    print("║  3. View app usage summary         ║")
    print("║  4. Set daily data limit           ║")
    print("║  5. Reset all app data             ║")
    print("║  6. Save and exit                  ║")
    print("╚════════════════════════════════════╝")
    print("Enter your choice (1-6): ", end="")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    usage, daily_limit = load_data()

    while True:
        print_menu()
        choice = input().strip()

        if choice == "1":
            session_mb = monitor_realtime(daily_limit)
            if session_mb > 0:
                log_it = input("\nLog this session to app list? (yes/no): ").strip().lower()
                if log_it == "yes":
                    app = input("Enter a name for this session (e.g. General Browsing): ").strip().title()
                    if app:
                        usage[app] = usage.get(app, 0) + round(session_mb, 2)
                        print(f"{round(session_mb, 2):.2f} MB logged under '{app}'.")

        elif choice == "2":
            add_usage(usage)

        elif choice == "3":
            display_summary(usage, daily_limit)

        elif choice == "4":
            new_limit = set_daily_limit()
            if new_limit > 0:
                daily_limit = new_limit

        elif choice == "5":
            reset_data(usage)

        elif choice == "6":
            save_data(usage, daily_limit)
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
