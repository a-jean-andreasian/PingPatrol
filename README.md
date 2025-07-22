![a](https://i.ibb.co/Spk964x/wmremove-transformed.png)

---

A lightweight Python tool for periodically pinging websites and monitoring their availability.  
Designed for use on Windows-based VPS systems or local machines without relying on external schedulers like `cron` or `Task Scheduler`.

---
## 🚀 Features

- 🕓 Built-in scheduler (no need for external tools)
- 🌐 Periodically pings a list of websites
- 🧵 Threaded execution - pings are run concurrently
- 🧠 Smart rescheduling for stable uptime monitoring
- 🪵 Simple log output with timestamps and HTTP status codes
- ⚙️ Easily extensible and readable

---
## 💻 Usage

1. **Add sources**

You will be prompted at runtime to enter the list of URLs to monitor. Alternatively, modify the script to load from a file or hardcode.

JSON structure for sources:

```json
[
  {"url": "https://example.com", "frequency": 10},
  {"url": "https://example2.com", "frequency": 15}
]
```


2. **Run the program**

```bash
python script.py
````

Sample output:

```
Do you want to add sources? (y/n): y
Enter URL: https://example.com
Enter URL: https://google.com
...

Starting monitor...
Fri Jul 19 14:00:01 2025: https://example.com -> 200
Fri Jul 19 14:00:01 2025: https://google.com -> 200
...
```

---
## 🔧 Customization & possible contribution

* Modify ping interval by adjusting the reschedule logic
* Add persistent URL storage or alerting (email/Telegram/etc.)
* Swap `requests` with `httpx` for async if needed

---

## 📦 Requirements

* Python 3.8+
* `requests`

Install dependencies:

```bash
pip install -r requirements.txt
```

---
## 📄 License

Creative Commons Attribution Share Alike 4.0 International, Armen-Jean Andreasian 2025
