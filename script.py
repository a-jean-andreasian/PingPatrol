import json
import sched
import threading
import time
from pathlib import Path
import requests
import os
import logging
from src.services.reporter import TelegramReporter
from src.helpers.load_env import load_env

load_env(path='config/.env')

# Constants ============================================================================================================
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 mb
ROTATION_THRESHOLD = 0.9

# Logger ===============================================================================================================
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Reporter =============================================================================================================
telegram_reporter = TelegramReporter(
    token=os.environ.get('TOKEN'),
    chat_id=os.environ.get('CHAT_ID')
)


# WebSource class to keep sources and frequencies ======================================================================
class WebSource:
    def __init__(self, url: str, frequency: int):
        self.url = url
        self.frequency = frequency

    def to_dict(self):
        return {"url": self.url, "frequency": self.frequency}


# Headers ==============================================================================================================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    )
}


# Logging stuff ========================================================================================================
class LoggingHandler:
    def __init__(self):
        self.last_report_time = 0
        self.report_cooldown = 3600  # 1 hour cooldown between reports

    def check_log_size(self):
        """Check if log file size exceeds threshold"""
        try:
            log_size = Path(LOG_FILE).stat().st_size
            current_time = time.time()

            if log_size > MAX_LOG_SIZE * ROTATION_THRESHOLD:  # trigger at 90% of max size
                if (current_time - self.last_report_time) > self.report_cooldown:
                    self._rotate_log_file()
                    self.last_report_time = current_time

        except Exception as e:
            logging.error(f"Error checking log size: {e}")

    def _rotate_log_file(self):
        """Rotate the log file when it gets too large, then empty the current log"""
        try:
            # Create rotated copy
            rotated_name = f"{LOG_FILE}.{int(time.time())}"
            Path(LOG_FILE).rename(rotated_name)

            # Recreate empty log file
            with open(LOG_FILE, 'w'):
                pass

            logging.info(f"Rotated log file to {rotated_name} and emptied current log")

            # Send rotation notification
            telegram_reporter.report(f"♻️ Log rotated: {rotated_name}\nCurrent log has been reset")

        except Exception as e:
            logging.error(f"Error rotating log file: {e}")
            telegram_reporter.report(f"❌ Log rotation failed: {str(e)}")


# Scheduler class to manage the pinging of sources =====================================================================
class WebSourceManager:
    SOURCES_FILE = Path("config/sources.json")

    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.sources: list[WebSource] = []
        self._load_sources()
        self.logging_handler = LoggingHandler()

    def _load_sources(self):
        if self.SOURCES_FILE.exists():
            try:
                with self.SOURCES_FILE.open() as f:
                    data = json.load(f)
                    for item in data:
                        self.sources.append(WebSource(**item))
            except json.JSONDecodeError:
                print(f"Error reading {self.SOURCES_FILE}")
                exit(0)
        else:
            with open(self.SOURCES_FILE, "w") as f:
                json.dump([], f)

    def _save_source(self):
        all_data = [s.to_dict() for s in self.sources]
        with self.SOURCES_FILE.open("w") as f:
            json.dump(all_data, f, indent=2)

    def add_source(self, url: str, frequency: int):
        src = WebSource(url, frequency)
        self.sources.append(src)
        self._save_source()
        self._schedule_ping(src, immediate=True)

    def _schedule_ping(self, src: WebSource, immediate: bool):
        delay = 0 if immediate else src.frequency
        self.scheduler.enter(delay, 1, self._ping_and_reschedule, argument=(src,))

    def _ping(self, src: WebSource):
        try:
            r = requests.get(src.url, timeout=5, headers=HEADERS)
            logging.info(f"{time.ctime()}: {src.url} -> {r.status_code}")
        except requests.RequestException as e:
            logging.error(f"{src.url} error: {e}")

        # Check log size after each ping
        self.logging_handler.check_log_size()

    def _ping_and_reschedule(self, src: WebSource):
        threading.Thread(target=self._ping, args=(src,), daemon=True).start()
        self._schedule_ping(src, immediate=False)

    def run(self):
        if not self.sources:
            print("No sources to monitor. Please add some first.")
            return

        for src in self.sources:
            self._schedule_ping(src, immediate=True)

        # Continuous, non-blocking run loop
        try:
            while True:
                self.scheduler.run(blocking=False)
                time.sleep(1)  # Sleep to prevent busy waiting that one second
        except KeyboardInterrupt:
            print("Monitoring stopped.")


# ----------- Main Program -----------
def keyboard_inter_decor(func):
    """
    Decorator to handle keyboard interrupts gracefully.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nScript stopped by user.")
            exit(0)

    return wrapper


@keyboard_inter_decor
def main():
    manager = WebSourceManager()

    log_file_path = Path(LOG_FILE).resolve()
    print(f"INFO: Press Ctrl+C to stop monitoring.\n"
          f"INFO: Check {log_file_path} for monitoring details.\n")

    answer = input("Do you want to add sources? (y/n): ").strip().lower()

    if answer == "y":
        while True:
            url = input("Enter website URL: ").strip()
            # URL Validation
            if not url.startswith("http://") and not url.startswith("https://"):
                print("URL must start with 'http://' or 'https://'.")
                continue
            if not url:
                print("URL cannot be empty.")
                continue

            # Frequency Validation
            try:
                freq = int(input("Enter ping frequency (in seconds): ").strip())
            except ValueError:
                print("Frequency must be a number.")
                continue

            if freq <= 0:
                print("Frequency must be a positive integer.")
                continue

            # Adding source
            manager.add_source(url, freq)

            cont = input("Add another? (y/n): ").strip().lower()
            if cont != "y":
                break
    print("Starting monitor...")
    manager.run()


if __name__ == "__main__":
    main()
