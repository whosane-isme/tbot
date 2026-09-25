# tbot — Website Telegram Notifier (Educational Prototype)

A small local demo of this request path:

```text
Browser page → JavaScript fetch() → FastAPI → Telegram Bot API → Telegram chat
```

The browser talks only to FastAPI. **Never put `TELEGRAM_BOT_TOKEN` in HTML or frontend JavaScript.** Anything sent to a browser can be inspected by its visitor. The backend keeps both Telegram settings in its `.env` file.

## Project files

```text
backend/
  main.py
  .env.example
  requirements.txt
  .gitignore
frontend/
  index.html
  style.css
  script.js
```

## 1. Set up Telegram

1. In Telegram, open **@BotFather**, send `/newbot`, follow its prompts, and copy the bot token it gives you. Keep the token private.
2. Open a conversation with your new bot and send `/start`. This gives the bot a chat in which it can message you.
3. In a browser, visit `https://api.telegram.org/botYOUR_TOKEN_HERE/getUpdates`, replacing the placeholder with your token. In the returned JSON, find `message` → `chat` → `id`. That number is your chat ID. If the result is empty, send `/start` to your bot and refresh the page.
4. Copy `backend/.env.example` to `backend/.env` and replace the placeholder values:

   ```env
   TELEGRAM_BOT_TOKEN=the_token_from_BotFather
   TELEGRAM_CHAT_ID=the_chat_id_number
   ```

   Do not commit or share `.env`. It is ignored by `backend/.gitignore`. The token is part of the backend's request URL to Telegram, so do not print that URL or put it in frontend code.

## 2. Start FastAPI

Open a terminal **inside the `backend` folder** (the folder containing `main.py`) and run:

```powershell
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can invoke the environment's Python directly as `.\.venv\Scripts\python.exe` for the pip and Uvicorn commands below.

Install the small dependency list:

```powershell
python -m pip install -r requirements.txt
```

Start the local API server, still in `backend`:

```powershell
uvicorn main:app --reload
```

Uvicorn is the local web server process. Visit `http://127.0.0.1:8000/health`; it should show `{"status":"ok"}`. FastAPI also provides interactive API documentation at `http://127.0.0.1:8000/docs`.

## 3. Test the API before the webpage

Use Postman as a test client:

1. Choose **POST** and enter `http://127.0.0.1:8000/event`.
2. Choose **Body → raw → JSON**.
3. Send this body:

   ```json
   {
     "event_type": "book_click",
     "page": "Postman Test"
   }
   ```

With valid Telegram credentials, the flow is **Postman → FastAPI → Telegram API → your Telegram chat**. Postman is only a testing client; it is not part of the finished browser flow. If credentials are missing, FastAPI logs the event and returns a readable `503` explaining what to configure. Invalid Telegram settings or a Telegram/network error produce a readable `502`.

Optional equivalent using curl from any terminal:

```sh
curl -X POST http://127.0.0.1:8000/event -H "Content-Type: application/json" -d "{\"event_type\":\"book_click\",\"page\":\"Postman Test\"}"
```

## 4. Open the demo page

Start FastAPI first, and leave its terminal running. Then use either option:

**Option A — VS Code Live Server:** Open the `frontend` folder and use Live Server to serve `index.html` at `http://localhost:5500`. The backend allows this local origin.

**Option B — Python's simple web server:** Open a second terminal **inside the `frontend` folder** and run:

```powershell
python -m http.server 5500
```

Then visit `http://localhost:5500`. The JavaScript sends requests to `http://127.0.0.1:8000`. The backend has a narrow local-development CORS allowlist for `localhost:5500` and `127.0.0.1:5500`; CORS lets this separate page call the API, but is not authentication or production security configuration.

On page load, the page sends `page_visit`. Click **Book Now** or **Contact Us** to send the other event types. The text below the buttons reports success or failure. Check the browser console and the FastAPI terminal for details if sending fails.

## How This Project Actually Works

When you click **Book Now**:

1. The browser loads `index.html`, which displays the room and the two buttons.
2. `script.js` runs and registers a click listener on the Book Now button.
3. You click Book Now; its listener calls `sendEvent("book_click")`.
4. `fetch()` creates an HTTP `POST` request to `http://127.0.0.1:8000/event`.
5. The request has a `Content-Type: application/json` header and a JSON body like `{"event_type":"book_click","page":"Hotel Demo"}`. JSON is a text format for structured data.
6. The request travels from the browser to the FastAPI server listening on your computer at port 8000.
7. FastAPI matches the method and path to `@app.post("/event")`. The decorator tells FastAPI which function handles POST requests for `/event`.
8. FastAPI reads the JSON body. Pydantic checks that `event_type` is one of the accepted names and supplies the page value.
9. Python prints the validated event in the backend terminal and makes a readable message with a timestamp generated on the backend.
10. The backend reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from its environment, then `httpx` sends a second HTTP `POST` request to Telegram's `sendMessage` API.
11. The bot token identifies the bot in the API URL; the chat ID tells Telegram where to deliver the message. Telegram returns an HTTP response to the backend.
12. FastAPI returns a JSON success response to the browser after Telegram accepts the message.
13. JavaScript reads that response and changes the page status to “Event sent successfully.” If an error occurs, it shows a failure status and logs details in the browser console.

If no Telegram credentials are configured, the backend still prints the event, then responds with a clear `503` instead of attempting the Telegram request. This lets you see that the browser-to-backend portion works before setting up Telegram.

## What each file owns

- `index.html` owns the page structure, room details, buttons, and status text.
- `style.css` owns the page's appearance.
- `script.js` owns button listeners, the page-visit event, the `fetch()` request, and visual feedback.
- `main.py` owns the FastAPI routes, request validation, message formatting, environment-variable reads, and Telegram HTTP request.
- `.env` (you create it from `.env.example`) owns your private Telegram token and chat ID. It is configuration, not source code.
- `requirements.txt` lists the Python packages needed to run the backend so they can be installed together.

The three files with the most important moving parts are `script.js`, `main.py`, and `.env`; `index.html` supplies the UI that creates the actions.

For a chapter-by-chapter path to rebuild the backend yourself, see [REBUILD_MAIN_PY.md](REBUILD_MAIN_PY.md). Each chapter adds and tests one idea before moving on.

## Questions

### What is the server in this project?

FastAPI, running under Uvicorn on your computer, is the server during local development. You do not need to rent a cloud server for this prototype.

### Why can't HTML alone safely send the Telegram message?

The bot token is a secret. A token put in HTML or JavaScript is delivered to visitors' browsers, where they can inspect it and use it. The backend keeps that token private and makes the Telegram request for the page.

### Is Postman required?

No. Postman simulates a client request and is useful for testing the API before connecting the webpage. The webpage itself calls the API with `fetch()`.

### Do I need a Telegram webhook?

No, not for sending these notifications. A Telegram webhook sends updates in the direction **Telegram → your backend**. This project sends in the opposite direction: **your backend → Telegram** using the Bot API's `sendMessage` method.

### Do I need `python-telegram-bot`?

No. This project only needs to make one ordinary HTTP request to Telegram's Bot API, so `httpx` makes the request directly without a Telegram framework.

### What changes if I host the website publicly?

Conceptually, the path becomes **public frontend → publicly reachable backend → Telegram**. The browser still must not receive the bot token. This prototype does not configure deployment.

### Can everything be free?

HTML, CSS, JavaScript, Python, FastAPI, and a local Uvicorn server are free to use. The Telegram Bot API is available for normal bot usage. No paid VPS is needed for this local prototype.

## Page-visit spam

This demo sends a notification every time the page loads, including reloads. Real applications often avoid notifying on every page load, debounce or deduplicate events, track sessions, filter bots, or notify only for meaningful actions. Those systems are intentionally outside this prototype.

## Reverse-engineering exercises

Try these in order. The exercise list gives tasks, not solutions:

1. Change the Telegram text when Book Now is clicked.
2. Add a third button to the HTML called “View Price”.
3. Make that button send `event_type = "price_click"`.
4. Add another field called `room_id` and send `room_id = "204"`.
5. Modify the Pydantic model to accept `room_id`.
6. Include `room_id` in the Telegram notification.
7. Delete the frontend `sendEvent()` function and rewrite it yourself.
8. Delete `POST /event` and rewrite the route yourself.
9. Delete the Telegram sending function and rebuild it using `httpx` yourself.
10. Recreate the whole small project in a new folder without looking at the original except when completely stuck.
