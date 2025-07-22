import json
import sched
import threading
import time
from pathlib import Path
import requests
import logging

# Logger ===============================================================================================================
logging.basicConfig(
    filename="ping_patrol.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
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

# Scheduler class to manage the pinging of sources =====================================================================
class WebSourceManager:
    SOURCES_FILE = Path("sources.json")

    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.sources: list[WebSource] = []
        self._load_sources()

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

    log_file_path = Path("ping_patrol.log").resolve()
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
