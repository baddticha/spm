import psutil
import time
import os
import datetime

# File to store gaming time
LOG_FILE = "steam_usage_log.txt"
DAILY_LIMIT = 4 * 3600  # 4 hours in seconds

def get_steam_processes():
    """Check if Steam games are running, excluding Steam client processes."""
    steam_processes = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            process_name = proc.info["name"].lower()
            # Exclude Steam client processes
            if "steam" in process_name and not ("steam.exe" in process_name or "steamwebhelper.exe" in process_name):
                steam_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return steam_processes


def read_logged_time():
    """Read logged time from file."""
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as f :
        data = f.readline().strip()
        try:
            log_date, time_spent = data.split(",")
            if log_date == datetime.date.today().isoformat():
                return int(time_spent)
        except ValueError:
            pass
    return 0

def write_logged_time(time_spent):
    """Write logged time to file."""
    with open(LOG_FILE, "w") as f:
        f.write(f"{datetime.date.today().isoformat()},{time_spent}")

def terminate_steam():
    """Terminate all Steam processes."""
    for proc in get_steam_processes():
        try:
            proc.terminate()
            proc.wait()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def monitor_steam_usage():
    """Monitor Steam usage and enforce time limits."""
    time_spent_today = read_logged_time()
    start_time = time.time()

    print("Monitoring Steam usage...")
    while True:
        steam_processes = get_steam_processes()
        if steam_processes:
            # Print the list of running Steam processes
            print("Running Steam processes:")
            for proc in steam_processes:
                print(f"PID: {proc.pid}, Name: {proc.name()}")
            # Update time spent if Steam is running
            elapsed_time = time.time() - start_time
            time_spent_today += elapsed_time
            write_logged_time(time_spent_today)
            start_time = time.time()

            if time_spent_today >= DAILY_LIMIT:
                print("Daily gaming limit reached. Closing Steam.")
                terminate_steam()
                break
        else:
            # Reset start time if Steam is not running
            start_time = time.time()

        time.sleep(10)  # Check every 10 seconds


if __name__ == "__main__":
    monitor_steam_usage()
