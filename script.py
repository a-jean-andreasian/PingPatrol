import json
import sched
import threading
import time
from pathlib import Path

import requests


class WebSource:
    def __init__(self, url: str, frequency: int):
        self.url = url
        self.frequency = frequency

    def to_dict(self):
        return {"url": self.url, "frequency": self.frequency}


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
            r = requests.get(src.url, timeout=5)
            print(f"{time.ctime()}: {src.url} -> {r.status_code}")
        except requests.RequestException as e:
            print(f"{time.ctime()}: {src.url} error: {e}")

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

if __name__ == "__main__":
    manager = WebSourceManager()

    answer = input("Do you want to add sources? (y/n): ").strip().lower()
    if answer == "y":
        while True:
            url = input("Enter website URL: ").strip()
            freq = int(input("Enter ping frequency (in seconds): ").strip())

            if freq <= 0:
                print("Frequency must be a positive integer.")
                continue

            manager.add_source(url, freq)

            cont = input("Add another? (y/n): ").strip().lower()
            if cont != "y":
                break

    print("Starting monitor...")
    manager.run()
