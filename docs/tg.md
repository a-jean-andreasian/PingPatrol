### ✅ 1. **Get `TELEGRAM_TOKEN`**

Create a bot with [@BotFather](https://t.me/BotFather) on Telegram:

* Open Telegram.
* Search for `@BotFather`.
* Send `/start`, then `/newbot`.
* Follow the prompts and it will give you a **bot token** like:

  ```
  123456789:ABCdefGhIJklMnopQRstuvWxyZ123456789
  ```

This is your `TELEGRAM_TOKEN`.

---

### ✅ 2. **Get `CHAT_ID`**

Use one of these ways:

#### Method A: Send a message and use `getUpdates`

1. Open a browser and go to:

   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
2. Send any message to your bot from your personal account.
3. Refresh that URL — you’ll see a JSON response.
4. Look for `"chat": {"id": 123456789, ...}` — that’s your `chat_id`.

#### Method B: Use this snippet:

```python
import requests

TOKEN = "your_bot_token"
updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
print(updates)
```

Then look inside for `"chat": {"id": ...}` like above.
