# Rebuild `main.py` From Scratch

This is a hands-on tutorial for recreating the small backend in this repository. The aim is to make each new piece understandable and testable before adding the next one.

The teaching approach is inspired by [Build Your Own X](https://github.com/codecrafters-io/build-your-own-x): learn by constructing a working thing one small piece at a time. Here, we are not rebuilding FastAPI or Telegram. We are rebuilding our tiny application and making the HTTP steps visible.

## Before you start

The backend lives in `backend/main.py`. Open a terminal in the `backend` folder when following backend commands. Keep the finished prototype as a reference; the chapters below show how to make simpler intermediate versions.

Start Uvicorn from that folder with:

```powershell
uvicorn main:app --reload
```

If you have not installed the dependencies yet, create and activate a virtual environment in `backend`, then install them:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The examples use the demo frontend already in `frontend/`. Keep real Telegram credentials out of Python and JavaScript. Chapter 10 explains the ignored `backend/.env` file. If your terminal is already running Uvicorn, stop it with Ctrl+C before replacing the file, then start it again.

---

# Chapter 0 — Mental model before code

## Goal

Know who is talking to whom before reading a route or a request.

## New concept: the two connections

```text
Browser (client) ──HTTP request──> FastAPI app (server)
                                      │
                                      └──HTTP request──> Telegram Bot API (server)
```

There are two separate HTTP conversations:

| Connection | Client | Server | What is being requested? |
|---|---|---|---|
| Browser → FastAPI | The browser running `script.js` | Our FastAPI app, served by Uvicorn | “Please record this page or button event.” |
| FastAPI → Telegram | Our Python backend | Telegram's Bot API | “Please send this text to this chat.” |

The word **server** describes a role in one conversation. FastAPI is a server when the browser calls it; it becomes an HTTP client when it calls Telegram.

## Important words, in this project

| Term | Meaning here |
|---|---|
| Client | The program that starts an HTTP request. The browser and, later, Python's `httpx` client each act as a client. |
| Server | A program waiting for requests. Uvicorn serves our FastAPI app; Telegram serves its Bot API. |
| HTTP | The request-and-response rules used for both connections. |
| Request | A message a client sends to a server. It has a method and an address; it may also have headers and a body. |
| Response | The server's reply, containing a status code and often data. |
| Route | A rule in our backend that connects an HTTP method and path to Python code, such as `POST /event`. |
| Endpoint | The address-and-method pair a client can call, such as `GET /health`. |
| GET | An HTTP request method commonly used to retrieve information. The browser sends a GET request when it opens `/health`. |
| POST | An HTTP request method commonly used to submit data for processing. JavaScript sends event JSON with POST. |
| JSON | Text for structured values, such as `{"event_type":"book_click"}`. |
| Request body | The optional data portion of a request. The event's JSON goes here. |
| Status code | A number in the response. `200` means success; `404` means the path was not found; `422` commonly means FastAPI could not validate the submitted data; `503` is used here when Telegram settings are missing. |
| API | A defined way for programs to ask another program to do something. `/event` is our API endpoint. |
| Third-party API | An API operated by another service. Telegram's Bot API is third-party from our app's point of view. |

## A common misunderstanding

GET is not “the server receives,” and POST is not “the server sends.” Both GET and POST are requests sent by a client. The method describes the kind of operation the client is asking the server to perform. The server receives either request and sends a response back.

## How to test this mental model

Open `http://127.0.0.1:8000/health` in a browser. The browser is the client for this GET request; FastAPI is the server. Later, Python's `httpx` client will send a POST request to Telegram. The roles reverse for that second conversation.

## Common mistake

Thinking “FastAPI sends to Telegram, so FastAPI is always the client.” Client and server are roles in a particular connection; FastAPI has a different role in each of the two connections above.

## Tiny exercise

For a Postman request to `/event`, name the client, server, method, and data format before clicking **Send**.

## What changed from the previous version?

Nothing yet. We built a map of the messages before writing code.

---

# Chapter 1 — The smallest FastAPI app

## Goal

Make one URL return a small answer.

## New concept

FastAPI maps an HTTP request to a Python function. Uvicorn runs the app and listens for the requests.

## Exact code to write

Replace `backend/main.py` with:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

## Explanation, line by line

- `from fastapi import FastAPI`: `fastapi` is an installed package, not part of Python's standard library. `FastAPI` is the class we use to create the web application. Without it, this file has no FastAPI app.
- `app = FastAPI()`: call the class to create one application object and store it in the variable `app`. Uvicorn will be given this object. `app` is just a variable name; the command later expects this name because we choose to name it `app`.
- `@app.get("/health")`: this is a decorator. The `@` syntax applies a function to the definition that follows. FastAPI's `.get()` registers the following function for GET requests whose path is `/health`. Remove the decorator and FastAPI will not know that the function handles this URL.
- `def health():`: define a normal Python function. FastAPI calls it when a matching request arrives. `health` is a name we chose.
- `return {"status": "ok"}`: return a Python dictionary. FastAPI converts this dictionary to a JSON response and normally uses status `200`.

`/health` is a path on the local API server, not a file path on your computer.

## How to run it

Run these commands while the terminal is inside `backend`:

```powershell
python -m pip install fastapi uvicorn
uvicorn main:app --reload
```

Read `main:app` as “import the `app` object from the Python module `main`.” The colon separates the module name from the variable name. `main` comes from `main.py`; `app` comes from `app = FastAPI()`.

Uvicorn is a separate package and process. FastAPI describes how the app behaves; Uvicorn listens for network connections (by default on port 8000) and passes requests to that app. `--reload` watches your Python file during development and restarts the server after a change. It is convenient while learning.

## How to test it

1. Open `http://127.0.0.1:8000/health` in a browser. You should see `{"status":"ok"}`.
2. Open `http://127.0.0.1:8000/docs`. FastAPI generated a page that can send test requests to the app.

## Common mistakes

- `Error loading ASGI app`: check that the terminal is in `backend`, the file is named `main.py`, and the variable is named `app`.
- Connection refused: Uvicorn is not running, or you opened the wrong port.
- A Python indentation error: the function's `return` must be indented under `def health():`.

## Tiny exercise

Change the returned status text to `"learning"`, save the file, and reload `/health`. With `--reload`, Uvicorn should restart automatically.

## What changed from the previous version?

We now have a running app and one GET route. There is no request body, Pydantic model, Telegram request, or browser event yet.

---

# Chapter 2 — Receive the simplest POST

## Goal

Send a small JSON object to FastAPI and see it in the terminal.

## New concept

Add one POST route that temporarily accepts a plain Python dictionary. We use `dict` first so we can see the raw incoming fields before adding validation.

## Exact code to write

Keep Chapter 1 and add the following route below `health()`:

```python
@app.post("/event")
def event(data: dict):
    print(data)
    return {"ok": True}
```

After adding it, `main.py` is:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def event(data: dict):
    print(data)
    return {"ok": True}
```

## Explanation

- `@app.post("/event")`: like `.get()`, this FastAPI decorator registers a route. The method is POST and the path is `/event`.
- `data: dict`: the function parameter is the JSON object FastAPI parsed from the request body. `dict` is a built-in Python type. This accepts dictionaries without describing which keys they must contain.
- `print(data)`: print the value in the terminal running Uvicorn. This is a simple learning aid, not a logging system.
- `return {"ok": True}`: FastAPI turns the returned dictionary into a JSON response.

The `dict` annotation helps FastAPI understand that this endpoint expects a JSON object body. We deliberately have not asked Pydantic to define event fields yet.

## How to test it

1. Open `/docs`.
2. Expand `POST /event`, choose **Try it out**, and enter:

   ```json
   {
     "event_type": "book_click"
   }
   ```

3. Choose **Execute**.

## Expected result

```text
request → FastAPI → Python dict → print() → JSON response
```

The docs page should show status `200` and `{"ok":true}`. The Uvicorn terminal should print `{'event_type': 'book_click'}`. The browser/docs page is the client; FastAPI is the server.

## Common mistakes

- Sending a JSON string such as `"book_click"` instead of an object such as `{"event_type":"book_click"}`.
- Putting the object in a query parameter instead of the request body.
- Reading the result in the wrong place: the response is in `/docs`; `print()` appears in the terminal.

## Tiny exercise

Add a `page` key to the request. Observe that the dictionary contains it without changing the Python code.

## What changed from the previous version?

We added one POST route. The health route still works. The event is only printed; Telegram is not involved.

---

# Chapter 3 — Connect the frontend

## Goal

Follow one click from JavaScript to the Python dictionary.

## New concept

The browser uses `fetch()` to send HTTP. `JSON.stringify()` turns a JavaScript object into JSON text for the request body. FastAPI parses that JSON text into Python values before calling `event(data)`.

## Exact code to inspect

The existing `frontend/script.js` contains this simplified request:

```javascript
const API_URL = "http://127.0.0.1:8000";

async function sendEvent(eventType) {
  const response = await fetch(`${API_URL}/event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type: eventType, page: "Hotel Demo" }),
  });
  console.log("Response status:", response.status);
}

sendEvent("book_click");
```

This is a small learning example; the real `script.js` calls it from button listeners and handles errors. Do not replace the working file with this snippet unless you are intentionally following along; the app still works as-is.

## Explanation

- `API_URL` is the address of FastAPI. The browser cannot guess which server owns `/event`, so the full address is used.
- `fetch(url, options)` asks the browser to make an HTTP request. The browser is the client.
- `method: "POST"` chooses the HTTP method. Both GET and POST are requests; this one submits event data.
- `Content-Type: application/json` tells FastAPI what format the request body uses.
- `JSON.stringify({...})` converts a JavaScript object into JSON text. `fetch` sends that text as the body.
- `await` waits for the browser's network operation to return a response before the next line reads `response.status`.
- On the Python side, `def event(data: dict)` receives the decoded object. The browser sent JSON text; FastAPI performed the conversion to a Python dictionary.

## How to run and test it

1. Run Uvicorn in `backend`.
2. In a second terminal, run `python -m http.server 5500` from `frontend`, or use VS Code Live Server at `http://localhost:5500`.
3. Open `http://localhost:5500` and click **Book Now**.
4. Open DevTools (F12) → **Network**, select the `/event` request, and inspect **Request Method**, **Request Payload**, **Status Code**, and **Response**. Watch the Uvicorn terminal too.

## Debug three different outcomes

### 1. JavaScript did not send anything

There is no `/event` entry in the Network list and nothing printed by Uvicorn. Look in the browser **Console** for a JavaScript error; check that the button ID in HTML matches the selector in JavaScript and that `script.js` loaded.

For example, with Uvicorn stopped, Chrome/Edge may show `TypeError: Failed to fetch` in the Console and `POST http://127.0.0.1:8000/event net::ERR_CONNECTION_REFUSED`. In Network, the request has `(failed)` instead of an HTTP status. Browser wording can differ, but the key clue is that there is no HTTP response status.

### 2. The browser sent a request, but FastAPI rejected it

There is an `/event` entry in Network with a non-success status. A missing route might show `404`; malformed JSON or invalid request data can show `422`. Inspect the **Response** tab for FastAPI's error details. The route may not print anything if FastAPI rejects the request before it calls the function.

For example, after Chapter 4, leaving out `event_type` can produce a response shaped like:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "event_type"],
      "msg": "Field required"
    }
  ]
}
```

The exact validation wording can vary by Pydantic version. The useful clues are Network status `422` and a detail that points at the missing body field.

### 3. FastAPI received it

Network shows a success status such as `200`, its response is `{"ok":true}`, and the Uvicorn terminal prints the dictionary. This confirms browser → FastAPI worked. At this chapter, no Telegram message should be sent.

Example evidence for the plain-dictionary chapter:

```text
Network: POST /event    Status: 200
Response: {"ok":true}
Uvicorn terminal: {'event_type': 'book_click', 'page': 'Hotel Demo'}
Console: no error
```

## Common mistakes

- Uvicorn is stopped: the browser cannot connect to port 8000.
- Wrong API address or port: Network shows a failed request such as `(failed)`; the Console reports a fetch/network error.
- Wrong JSON header: the server may not interpret the body as expected.
- Looking for `print()` in the browser: Python output belongs to the backend terminal.

## Tiny exercise

Change the page value to `"My first fetch"`. Find that exact text in the Network request payload and then in the Python terminal.

## What changed from the previous version?

The backend did not change. We added a browser client to make the same POST request that `/docs` made manually.

---

# Chapter 4 — Add Pydantic

## Goal

Describe the shape of a valid event instead of accepting any dictionary.

## New concept

Pydantic is the data validation library FastAPI uses for request models. The model says which fields to expect and what types they should have.

## Exact code changes

Add the import and class near the top of `main.py`:

```python
from pydantic import BaseModel


class Event(BaseModel):
    event_type: str
    page: str = "Hotel Demo"
```

Then change the route parameter only:

```python
@app.post("/event")
def event(data: Event):
    print(data)
    return {"ok": True}
```

**Before:** `def event(data: dict):`

**After:** `def event(data: Event):`

The rest of the route is still the same. The `Event` class is a schema: it describes the JSON shape. `BaseModel` is from Pydantic, not Python. `class Event(BaseModel)` defines a new model based on Pydantic's model behavior. The annotation `event_type: str` says this field should be text. `page: str = "Hotel Demo"` says page is text and supplies a default if a request leaves it out.

Pydantic checks incoming data and makes the fields available as `data.event_type` and `data.page`. Without this model, a plain dict accepts arbitrary keys and values and your code has to check them manually. We could write those checks ourselves, but Pydantic makes this small shape explicit and integrates with FastAPI's error response and docs.

## How to test it

In `/docs`, send:

```json
{"event_type":"book_click","page":"Postman Test"}
```

Expected: `200`, printed validated event, and `{"ok":true}`.

Then send:

```json
{"page":"Missing event name"}
```

Expected: `422 Unprocessable Entity`, because `event_type` is required. FastAPI/Pydantic return the error before calling your route function, so the event is not printed.

## Common mistakes

- Forgetting `from pydantic import BaseModel` causes `NameError` when Python reads the class.
- Sending a field with a different type can result in validation errors or conversion depending on the input. Use ordinary strings in these first requests.
- Reading fields from the model with dictionary brackets: use `data.event_type` for a Pydantic model; dictionaries use `data["event_type"]`.

## Tiny exercise

Leave `page` out of the request. What value does the model provide for `data.page`?

## What changed from the previous version?

**Before:** the function received a general-purpose dictionary. **After:** it receives an `Event` object, with a required text `event_type` and a default page. This adds validation and field access; the route still prints and responds without Telegram.

---

# Chapter 5 — Restrict event types

## Goal

Reject event names that this tiny demo does not know about.

## New concept

`Literal` is from Python's standard-library `typing` module. It narrows a field from “any string” to one of the listed strings.

## Exact code change

Add the import:

```python
from typing import Literal
```

Then change one field:

**Before:**

```python
event_type: str
```

**After:**

```python
event_type: Literal["page_visit", "book_click", "contact_click"]
```

## Explanation

`str` accepts values like `"book_click"`, `"pizza_click"`, or `"typo"`. The `Literal[...]` annotation tells Pydantic that only the exact listed strings are valid. Remove `Literal` and the rule goes away. We could write an `if` statement to check the string ourselves; this declaration lets Pydantic perform that check before our route runs.

FastAPI receives and routes the HTTP request. Pydantic validates the request data against the model. When validation fails, FastAPI formats the validation problem as an HTTP response, usually `422`.

## How to test it

In `/docs`, send `{"event_type":"book_click"}`. It should work. Then send `{"event_type":"pizza_click"}`. It should return `422`; the error response identifies the allowed values. The route's `print()` should run only for the valid event.

## Common mistakes

- Capitalization matters. `Book_Click` is not the same string as `book_click`.
- A valid JSON body can still be an invalid event. JSON parsing and model validation are different steps.

## Tiny exercise

Temporarily remove one allowed name from `Literal`, reload `/docs`, and try that event again. Restore it afterward.

## What changed from the previous version?

Just the annotation changed from `str` to `Literal[...]`. The model now rejects an unknown event before the route prints it.

---

# Chapter 6 — Format a message without Telegram

## Goal

Turn a validated event into readable message text, and inspect that text locally.

## New concept

A regular Python function can transform one value into another. We will create a message and print it before making any network request.

## Exact code to add

Add this function above the POST route:

```python
def make_telegram_message(event: Event) -> str:
    messages = {
        "page_visit": ("🌐 Website Event", "Page Visit"),
        "book_click": ("🔔 Website Event", "Book Now Clicked"),
        "contact_click": ("📩 Website Event", "Contact Button Clicked"),
    }

    icon_and_title = messages[event.event_type]
    message = (
        f"{icon_and_title[0]}\n\n"
        f"Event: {icon_and_title[1]}\n"
        f"Page: {event.page}"
    )
    return message
```

Change the route to call it:

```python
@app.post("/event")
def event(data: Event):
    print(data)
    message = make_telegram_message(data)
    print(message)
    return {"ok": True}
```

## Explanation

- `def make_telegram_message(...)` defines a function. `event: Event` documents the expected input model; `-> str` documents that the function returns text. These annotations help readers and tools; Python does not enforce the return annotation at runtime by itself.
- `messages` maps each allowed event name to a heading and a human-readable label. Since Chapter 5 restricts the names, each valid name has a matching entry.
- `messages[event.event_type]` uses the event name to select its heading and label.
- The `f"..."` strings insert values. `\n` means a line break in the resulting message.
- `return message` hands the constructed text back to the caller.
- The route stores and prints the returned text. No Telegram request exists yet.

Separating formatting from receiving is useful because the HTTP route can stay focused on the request while this function focuses on the words we want to send. For now, this is just two simple functions in one file; no extra architecture is needed.

## How to test it

Send each of the three valid event names through `/docs`. The terminal should show the input model and a matching formatted message. The browser/docs response should still be `{"ok":true}`.

## Common mistakes

- Misspelling a key in `messages` means Python raises `KeyError` when that event arrives.
- Seeing `\\n` as two characters usually means the backslash was escaped twice. In the code above, `\n` becomes a line break.

## Tiny exercise

Change only the visible label for `book_click`, then send that event and inspect the terminal.

## What changed from the previous version?

We added a pure formatting step and a second `print()`. The HTTP request still does not leave our computer for Telegram.

---

# Chapter 7 — Add backend time

## Goal

Put the time the backend handled the event into the message.

## New concept

Python's standard library includes `datetime`; no extra package is needed for this timestamp.

## Exact code changes

Add this import:

```python
from datetime import datetime, timezone
```

Inside `make_telegram_message`, before constructing `message`, add:

```python
timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
```

Add a line to the message:

```python
f"Time: {timestamp}"
```

The returned message portion now looks like:

```python
message = (
    f"{icon_and_title[0]}\n\n"
    f"Event: {icon_and_title[1]}\n"
    f"Page: {event.page}\n"
    f"Time: {timestamp}"
)
```

## Explanation

- `datetime` represents a date and time; `timezone` provides timezone information. Both come from Python itself.
- `datetime.now(timezone.utc)` asks for the current time with UTC timezone information.
- `.isoformat(timespec="seconds")` turns it into readable, consistent text with seconds.
- `.replace("+00:00", "Z")` uses `Z` as the familiar UTC marker.

The browser could include its own time, but a visitor can change their device clock or send a made-up timestamp. Generating time on the backend records when this backend processed the event. It does not prove when a human actually clicked; it simply avoids trusting a client-provided clock.

## How to test it

Send an event and inspect the terminal's formatted message. It should now have a `Time:` line ending in `Z`.

## Common mistakes

- `NameError: datetime is not defined`: add the import at the top.
- The time may differ from your local clock because it is UTC. For this demo we use UTC to avoid adding another library or timezone setting.

## Tiny exercise

Temporarily print `timestamp` by itself, then compare that value with the `Time:` line in the message.

## What changed from the previous version?

We added one standard-library import and one backend-created string to the Telegram message. There is still no Telegram request.

---

# Chapter 8 — What Telegram needs (conceptually)

## Goal

Connect the request we already understand to the shape Telegram expects.

## New concept

Telegram is another HTTP API. Our backend becomes a client and sends a POST request containing a destination chat ID and message text.

The request has this general shape:

```text
POST https://api.telegram.org/bot<TOKEN>/sendMessage
Content-Type: application/json
```

JSON body:

```json
{
  "chat_id": "<CHAT_ID>",
  "text": "🔔 Website Event\n\nEvent: Book Now Clicked"
}
```

The token identifies the bot; `chat_id` identifies the destination; `text` is the message. These are placeholders, not usable credentials. Do not paste a real token into Python source, JavaScript, README examples, or Git. A real token in browser code is visible to visitors.

## Explain both requests

```text
Browser (client) → FastAPI (server): event JSON
FastAPI (client) → Telegram (server): chat ID and message text
```

HTTP is the same request/response idea twice. The difference is who starts each request and what the body means.

## How to test this concept

No Telegram request is made in this chapter. Look at the formatted text from Chapter 6 and identify which parts will become `chat_id` and `text`. The `chat_id` is not part of the event message itself; it is delivery configuration.

## Common mistakes

- Thinking Telegram calls our backend to send a normal bot message. That would be a webhook/update flow. This app makes an outbound request to Telegram.
- Putting the bot token in `script.js`: everything sent to the browser can be inspected.

## Tiny exercise

Draw both arrows and label the client on each arrow. Explain why FastAPI changes roles.

## What changed from the previous version?

Nothing in the running app yet. We described the outbound request before choosing a Python HTTP library.

---

# Chapter 9 — Send the HTTP request with `httpx`

## Goal

Make the backend send the formatted message to Telegram.

## New concept: an HTTP client library

`httpx` is an external Python package for sending HTTP requests. We choose it because the finished route is `async`, and `httpx.AsyncClient` lets the route wait for network I/O without blocking in the same way a synchronous call would. It also offers a simple `.post(..., json=...)` API.

Alternatives:

- `requests` is popular and straightforward, but its usual API is synchronous. If a synchronous request runs inside an `async def` route, it blocks that worker while waiting. We could instead make the route synchronous and use `requests`; then the code would be simpler in one sense but its execution style would differ.
- Python's standard-library `urllib` can send HTTP without installing a package. It is more manual for this JSON request and does not provide the same beginner-friendly async client interface. Avoiding a dependency is possible, but would distract from this project's async request flow.

FastAPI is a third-party web framework; Pydantic validates request data; `httpx` is the HTTP client for the outbound Telegram request. Uvicorn is the server process. Each package has a separate job.

## Exact code to add

Add this import:

```python
import httpx
```

For this teaching checkpoint, add the following simple function with placeholders. Do not substitute a real token in source code:

```python
async def send_telegram_message(message: str) -> None:
    token = "<TOKEN>"
    chat_id = "<CHAT_ID>"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"chat_id": chat_id, "text": message},
        )

    print(response.status_code)
    print(response.text)
```

Then change the route to:

```python
@app.post("/event")
async def event(data: Event):
    message = make_telegram_message(data)
    await send_telegram_message(message)
    return {"attempted": True}
```

## Explanation

- `async def` defines a function that can pause while waiting for an operation, such as network I/O.
- `httpx.AsyncClient()` creates an async HTTP client. `async with` opens it and closes its network resources when the indented block ends; that pattern is called a context manager.
- `await client.post(...)` sends a POST request and pauses this coroutine until the HTTP response arrives. `json=...` asks httpx to encode that Python dictionary as a JSON request body and set the JSON content type.
- `response` contains the HTTP response from Telegram. It has properties such as `status_code` and `text`.
- The route must also be `async def` because it awaits the send function. Its `await` means “wait for that coroutine to finish here.”

`async` and `await` do not make the request happen in the background; we still wait for Telegram's response before returning success to the browser. They let the server yield while waiting, so it can make better use of time handling other requests.

## How to test it

With placeholders, Telegram will reject the request. That is expected: this checkpoint is to see an HTTP response and the route-to-client sequence. The temporary `{"attempted": true}` response means only that our function finished making its attempt; it does **not** mean Telegram accepted the message yet. Chapter 12 adds that distinction. For actual delivery, proceed to Chapter 10 and set real credentials in the ignored environment file. Never claim a message was delivered merely because the HTTP request was attempted; check Telegram's response.

## Common mistakes

- `ModuleNotFoundError: No module named 'httpx'`: install the project's requirements (or `python -m pip install httpx` in the active environment).
- Using `await` inside a normal `def`: `await` belongs inside `async def`.
- Forgetting `await` before `client.post`: then the code has not waited for the response when it tries to read response fields.
- Treating an HTTP response as proof Telegram accepted the message: inspect the status and Telegram's JSON `ok` field in Chapter 12.

## Tiny exercise

Point at the exact line that sends a network request. Point at the exact line that waits for Telegram's answer.

## What changed from the previous version?

We added an outbound HTTP client and changed the POST route to async. FastAPI still receives the same event; now the backend sends its formatted text to Telegram.

---

# Chapter 10 — Move secrets to environment variables

## Goal

Remove credential placeholders from Python source and read private settings from the backend process environment.

## New concepts

An **environment variable** is a named text value available to a running process. Python's built-in `os.getenv()` reads one. A `.env` file is a simple text file that `python-dotenv` can load into the process environment at startup.

The browser runs `frontend/script.js`; the backend runs Python under Uvicorn. The browser can download frontend files, but it does not download backend Python or `backend/.env`. This separation is why the Telegram token belongs on the backend. The code must still never put the token into a response or print it.

## Exact code changes

Add the imports:

```python
import os
from dotenv import load_dotenv
```

Call the loader once near the top, after imports and before `os.getenv` is used:

```python
load_dotenv()
```

Change the first two lines inside `send_telegram_message`:

**Before (placeholder only):**

```python
token = "<TOKEN>"
chat_id = "<CHAT_ID>"
```

**After:**

```python
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
```

Create `backend/.env` beside `main.py` using this format:

```env
TELEGRAM_BOT_TOKEN=put_your_private_bot_token_here
TELEGRAM_CHAT_ID=put_your_chat_id_here
```

The lines above are placeholders; replace them in your local ignored `.env` file. Do not put actual values in this tutorial. `backend/.gitignore` excludes `.env` and the local virtual environment from Git.

## Explanation

- `python-dotenv` is an external package, installed as `python-dotenv` but imported as `dotenv`. `load_dotenv()` reads `.env` and puts its values into the environment of this Python process. It does not send the file anywhere.
- `os` is part of Python's standard library. `os.getenv("TELEGRAM_BOT_TOKEN")` asks the process environment for that named value. It returns `None` if the name is not present.
- Uvicorn starts the Python process; `load_dotenv()` runs as the module is imported. If you edit `.env` after startup, restart Uvicorn so the new process reads the updated file.
- `.env` is not a special encrypted file; it is plain text. Its privacy comes from keeping it on your machine and excluding it from Git, not from a magic file format.

Why not set these strings directly in `main.py`? Source code is easy to commit, copy, or show. Keeping settings outside code makes it less likely to publish a credential and lets the same code use different settings on different machines.

## Why F12 does not reveal backend `.env`

F12 can inspect files and requests delivered to the browser, such as `index.html`, `style.css`, and `script.js`. The `.env` file is read by the backend process and is not part of the page response. A server could accidentally reveal a secret if it returned it in JSON, embedded it into HTML, or logged/sent it elsewhere; keep it out of those paths too.

## How to test it

Restart Uvicorn from `backend`. Check that it starts without an import error. With both values configured, send a valid event through `/docs`; the backend should contact Telegram. If Telegram rejects it, Chapter 12 explains how to read the error. Do not post credential values in a terminal transcript or issue.

## Common mistakes

- Naming the file `.env.txt` by accident. Ensure File Explorer is showing file extensions and the name is exactly `.env`.
- Placing `.env` in the project root while running `load_dotenv()` from `backend`. Put it beside `main.py` as shown, or deliberately configure another path.
- Editing `.env` but not restarting Uvicorn.
- Committing `.env`. Verify with `git check-ignore backend/.env`; it should print the ignored path. Never commit a real token even if you later delete it from the latest commit.

## Tiny exercise

Temporarily rename one environment variable in `.env`, restart the server, and observe that the backend process does not receive the expected setting. Restore the correct name afterward; Chapter 11 will make the failure message clearer.

## What changed from the previous version?

The request still uses the same URL and JSON. Only the source of the token and chat ID changed: they now come from the backend environment instead of code literals.

---

# Chapter 11 — Explain missing credentials

## Goal

Return a readable HTTP error if the backend cannot make a Telegram request because configuration is absent.

## New concept

FastAPI's `HTTPException` means “stop handling this request and send an HTTP error response with this status and detail.” It is from FastAPI, not Python itself.

## Exact code change

Add this import:

```python
from fastapi import HTTPException
```

After reading `token` and `chat_id`, add:

```python
if not token or not chat_id:
    raise HTTPException(
        status_code=503,
        detail="Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in backend/.env.",
    )
```

## Explanation

The route can receive an event even when Telegram is not configured. This condition checks whether either value is missing or empty. `raise` stops the normal path. FastAPI catches its `HTTPException` and turns it into an HTTP response containing the selected status and detail.

We use `503 Service Unavailable` because our event endpoint cannot complete its intended notification while a required backend dependency is unconfigured. `500` could also be argued if we treat this as a server misconfiguration; `424` is sometimes used for dependency failures but is less familiar. The important point for this demo is a clear non-success status and useful safe detail. The token itself must never be part of the error message.

## Request lifecycle when credentials are missing

```text
Browser sends POST /event
  → FastAPI parses and validates event
  → backend finds a credential missing
  → FastAPI responds 503 with safe detail
  → JavaScript sees response.ok === false
  → page shows its failure status; Console has diagnostic information
```

In the current `script.js`, it reads the JSON response detail, throws a JavaScript error for non-success responses, then displays “Failed to send event. Check the browser console.” The Network panel shows `503`; the Uvicorn terminal still shows the received event.

## How to test it

Temporarily rename `backend/.env` so `load_dotenv()` cannot find it, restart Uvicorn, and send a valid event. Expect `503` and the missing-settings detail. Restore `.env` afterward and restart. Avoid copying a real token into a screenshot or transcript.

## Common mistakes

- Returning `{"success": false}` with status `200`: clients often treat HTTP 200 as a successful request. An error status makes the network result clear.
- Telling the browser the token value: only say which setting is absent.
- Expecting Pydantic to catch missing Telegram credentials: Pydantic checks request data, not server configuration.

## Tiny exercise

In DevTools Network, find the `503` response. Then name what appeared in the browser, the Network panel, and the backend terminal.

## What changed from the previous version?

We added one explicit configuration check before constructing the Telegram URL. Valid configured requests follow the same path; missing settings stop with a readable `503`.

---

# Chapter 12 — Handle Telegram and network errors

## Goal

Distinguish Telegram refusing a request from Python being unable to reach Telegram.

## New concepts

`try` marks code that might fail. `except` handles a particular kind of exception. `httpx` defines `HTTPStatusError` for an HTTP error response after `raise_for_status()`, and `RequestError` for a request that could not complete, such as a connection or timeout error.

## Add handling gradually

First, after `client.post(...)`, add:

```python
response.raise_for_status()
```

That line turns HTTP status codes such as 401 or 500 into an `httpx.HTTPStatusError`. Then put the network operation and status check in a `try` block and add two `except` clauses:

```python
try:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            json={"chat_id": chat_id, "text": message},
        )

    response.raise_for_status()
    telegram_result = response.json()
    if not telegram_result.get("ok"):
        raise HTTPException(status_code=502, detail="Telegram did not accept the message.")

except httpx.HTTPStatusError as error:
    print(f"Telegram returned HTTP {error.response.status_code}.")
    raise HTTPException(
        status_code=502,
        detail="Telegram rejected the message. Check your bot settings.",
    ) from None

except httpx.RequestError as error:
    print(f"Could not reach Telegram: {error}")
    raise HTTPException(
        status_code=502,
        detail="Could not reach Telegram. Check your internet connection.",
    ) from None
```

`timeout=10.0` limits how long this demo waits for Telegram before treating the request as a network problem. A Telegram API response can have HTTP status 200 but JSON `{"ok": false}`; we check that API-level result too.

`from None` hides the chained low-level exception from the response traceback. The message sent to the browser is our safe, readable detail; the terminal prints a little more information. Do not print the request URL, because it contains the token.

## Four failure locations

| Failure | Where it happens | What I see | How I debug it |
|---|---|---|---|
| Telegram rejects the request | Telegram received it but does not accept the credentials or message | Browser gets `502`; FastAPI terminal prints Telegram's HTTP status; Telegram sends nothing | Check bot token, chat ID, and whether the bot can message that chat. Never log the full URL. |
| Network/timeout failure | `httpx` cannot complete a connection to Telegram | Browser gets `502`; terminal says it could not reach Telegram | Check internet access and the terminal error. |
| Our code rejects the request | FastAPI/Pydantic rejects invalid input, or our credentials check raises an error | Usually `422` for validation or `503` for missing configuration | Inspect Network → Response, and see whether the route printed the event. |
| Browser cannot reach FastAPI | Browser-to-backend connection, address, port, or CORS check | Fetch fails; Console reports a network/CORS error; Network may show `(failed)` | Confirm Uvicorn is running at the URL in `script.js`; check CORS in Chapter 13. |

`HTTPStatusError` and `RequestError` only handle the two `httpx` cases. They do not catch Pydantic's validation response or browser errors; those happen in different layers.

## How to test it

With valid Telegram settings, send a valid event and confirm that Telegram returns an accepted result and you receive the message. If you have no valid credentials, do not claim end-to-end success. You can still inspect the missing-credential response and reason through the other rows.

## Common mistakes

- Calling `raise_for_status()` and assuming that catches HTTP 200 with Telegram JSON `ok: false`. It does not; the JSON check is separate.
- Returning or printing the Telegram URL, which contains the bot token.
- Using a broad `except Exception` that hides which layer failed. These two specific `httpx` exceptions teach us more.

## Tiny exercise

In the table, point to the layer responsible for each symptom: `422`, `503`, `502`, and browser `(failed)`.

## What changed from the previous version?

We added a timeout, HTTP status checking, a Telegram JSON check, and two targeted exception handlers. Normal successful flow is unchanged.

---

# Chapter 13 — CORS, carefully

## Goal

Allow the local page served on one address to call the API served on another address.

## New concept: origin

An origin is the combination of **scheme + host + port**. For example:

```text
http://localhost:5500
└scheme └host      └port
```

The frontend at `http://localhost:5500` and the backend at `http://127.0.0.1:8000` have different origins. A browser enforces Cross-Origin Resource Sharing (CORS) rules before allowing JavaScript to read cross-origin responses. The browser may first send an `OPTIONS` preflight request to ask whether the POST with JSON is allowed.

CORS is a browser rule. It is not authentication. Allowing an origin does not stop someone from using curl or Postman to call the API directly, and it does not prevent every kind of attacker from making requests.

## Exact code to add

Add the middleware import:

```python
from fastapi.middleware.cors import CORSMiddleware
```

After `app = FastAPI()`, add:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

## Explanation of each setting

- `CORSMiddleware` is FastAPI/Starlette middleware: code that sees requests and responses around the route. Remove it and the browser may block this cross-origin call even though curl can still reach the API.
- `allow_origins` lists the exact local page origins we use. Scheme and port matter; `localhost` and `127.0.0.1` are different host strings.
- `allow_methods` says which methods are allowed from those origins. The browser uses POST for an event; GET is included for the health check.
- `allow_headers` permits the JSON `Content-Type` header used by `fetch()`.

This is a narrow local-development setting. Do not replace it with a wildcard and call that production security. CORS is not a login system; a public application still needs to think separately about who may call its backend and how to limit abuse.

## How to test it

Start both local servers and click a button. In Network, look for an `OPTIONS` preflight (the browser may cache it), then the `POST /event`. If you open the page from an origin not in the list, the browser Console reports a CORS error and may not expose the response to JavaScript. Test via curl/Postman and you may still see the backend respond; that does not disprove the browser's CORS message.

## Common mistakes

- Allowing `http://localhost:5500/` with a trailing slash; origin strings normally have no path.
- Serving frontend on another port such as 5501 without adding that exact origin.
- Treating CORS as protection against curl/Postman. Those clients do not enforce browser CORS rules.

## Tiny exercise

Temporarily remove the CORS middleware, reload the page, and predict the Console and Network behavior. Restore it and compare with a direct Postman request.

## What changed from the previous version?

We added middleware that allows the two local frontend origins. The route code and Telegram request did not change.

---

# Chapter 14 — Rebuild the final `main.py`

## Goal

Put the pieces together after understanding each responsibility.

## Before reading the final file, ask yourself

- What does FastAPI do, and what does Uvicorn do?
- What is a route? What are GET and POST?
- Where is the request body, and how does JSON become Python data?
- What does Pydantic validate? What does `Literal` add?
- What does an HTTP status code describe?
- Why does `httpx` exist, and why do we await it?
- Where do the environment variables come from?
- Which system is the client in the Telegram request?
- What does CORS allow, and what does it not protect?

If one answer is fuzzy, revisit that chapter first. The purpose is understanding, not racing to paste this file.

## Complete file

This is the finished educational prototype. It combines the same small steps; it does not add a database, framework layers, or extra files.

```python
import os
from datetime import datetime, timezone
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load backend/.env into the environment of this Python process.
load_dotenv()

app = FastAPI()

# Let the locally served demo page call this backend from its own local origin.
# This is browser CORS behavior, not authentication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Event(BaseModel):
    # Pydantic validates the JSON body before the route function runs.
    event_type: Literal["page_visit", "book_click", "contact_click"]
    page: str = "Hotel Demo"


@app.get("/health")
async def health():
    return {"status": "ok"}


def make_telegram_message(event: Event) -> str:
    messages = {
        "page_visit": ("🌐 Website Event", "Page Visit"),
        "book_click": ("🔔 Website Event", "Book Now Clicked"),
        "contact_click": ("📩 Website Event", "Contact Button Clicked"),
    }
    icon_and_title = messages[event.event_type]

    # The backend supplies the time instead of trusting a browser clock.
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    message = (
        f"{icon_and_title[0]}\n\n"
        f"Event: {icon_and_title[1]}\n"
        f"Page: {event.page}\n"
        f"Time: {timestamp}"
    )
    return message


async def send_telegram_message(message: str) -> None:
    # These values are private backend configuration; never put the bot token in JS.
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise HTTPException(
            status_code=503,
            detail="Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in backend/.env.",
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={"chat_id": chat_id, "text": message},
            )

        response.raise_for_status()
        telegram_result = response.json()
        if not telegram_result.get("ok"):
            raise HTTPException(status_code=502, detail="Telegram did not accept the message.")

    except httpx.HTTPStatusError as error:
        # Do not print or return the URL: the URL contains the token.
        print(f"Telegram returned HTTP {error.response.status_code}.")
        raise HTTPException(
            status_code=502,
            detail="Telegram rejected the message. Check your bot settings.",
        ) from None

    except httpx.RequestError as error:
        print(f"Could not reach Telegram: {error}")
        raise HTTPException(
            status_code=502,
            detail="Could not reach Telegram. Check your internet connection.",
        ) from None


@app.post("/event")
async def receive_event(event: Event):
    # FastAPI turns the JSON request body into the validated Event model.
    print(f"Received event: {event.model_dump()}")
    message = make_telegram_message(event)
    await send_telegram_message(message)
    return {"success": True, "event_type": event.event_type}
```

## What each import is doing

| Import | Comes from | Why it is here | If removed |
|---|---|---|---|
| `os` | Python standard library | Reads process environment values with `os.getenv`. | The token and chat ID would not be read this way. |
| `datetime`, `timezone` | Python standard library | Makes a UTC timestamp on the backend. | Remove the import and time formatting, or Python will report a missing name. |
| `Literal` | Python standard library `typing` | Restricts event names in the Pydantic field. | `str` would accept unknown event names. |
| `httpx` | External package | Sends the backend's outbound HTTP request to Telegram. | No Telegram request can be made through this code. |
| `load_dotenv` | External package `python-dotenv` | Reads the local `.env` file into this process's environment. | Values must already be set in the shell environment. |
| `FastAPI`, `HTTPException` | External package FastAPI | Creates the app and returns intentional HTTP errors. | No FastAPI app or readable intentional HTTP error. |
| `CORSMiddleware` | FastAPI's Starlette middleware | Allows the listed local browser origins. | The browser may block the cross-origin page request. |
| `BaseModel` | External package Pydantic | Defines and validates the event body. | The route would need manual checks on a dictionary. |

The type annotations help explain what data is expected. The `async` route and `await` call match the async HTTP client. The route calls the formatter, then the sender, in that order so you can read the path in ordinary Python steps.

## How to run and test the final version

From `backend`, start:

```powershell
uvicorn main:app --reload
```

Check `GET http://127.0.0.1:8000/health`. Then send a valid POST in `/docs` or Postman. With valid credentials, Telegram should accept the message. Without credentials, `/event` returns `503` and explains which settings to add. With a bad Telegram response or a network problem, the backend returns a readable `502`.

To test the browser, serve `frontend` at `http://localhost:5500` and click a button. A page load sends `page_visit`. In DevTools Network, observe the browser's request to FastAPI; in the backend terminal, observe its event print; in Telegram, observe delivery. This is three different places where evidence appears for three different steps.

## What changed from the previous version?

Nothing new was introduced here. This chapter assembles the ideas you already tried into the final file. The finished code has a few extras for a complete prototype—UTC timestamp, missing-configuration check, timeout, Telegram response check, and local CORS—but each appeared in an earlier chapter.

---

# Rebuild It Without Looking

Close this document and use only this blank-step checklist. Try to write and run each stage before checking the original project:

1. Create a FastAPI app object.
2. Create `GET /health` and make it return a dictionary.
3. Create `POST /event` and accept a plain dictionary.
4. Print the dictionary and return a small JSON response.
5. Replace the dictionary parameter with a Pydantic `Event` model.
6. Restrict the event name to the three supported strings.
7. Write a function that converts an event to a readable message.
8. Add a UTC timestamp to that message.
9. Send a Telegram POST request using `httpx`.
10. Move token and chat ID into environment variables loaded from `.env`.
11. Return a clear error when credentials are missing.
12. Handle Telegram HTTP errors and network failures separately.
13. Add local CORS settings for the frontend.
14. Run `/health`, test `/event` in `/docs`, then test a browser button.

Do not copy the checklist's numbering as code. Try to recall what each item needs, and use the earlier chapters only when you get stuck.

---

# Break-It Exercises

For **every** exercise, predict three things before changing anything:

1. What will the browser Console show?
2. What will the Network panel show (request, status, or failed connection)?
3. What will the Uvicorn terminal show?

Then make only the stated change, test it, and restore the code before moving on.

## 1. Backend port changes to 8001; JavaScript stays at 8000

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

If Uvicorn listens on 8001 while `API_URL` still points at 8000, the browser fetch cannot connect. Console shows a fetch/network error. Network shows a failed request, often `(failed)` with no HTTP status. The Uvicorn terminal on port 8001 shows no `/event` request because the browser sent it to 8000.
</details>

## 2. Remove `book_click` from `Literal`

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

The browser reaches FastAPI, but Pydantic rejects the body. Network shows `422` and a validation response. The frontend's catch path shows its failed status and logs the error. The route's `print()` does not run because validation happens before the route function.
</details>

## 3. Rename backend `/event` to `/events` only

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

JavaScript still POSTs to `/event`. Network shows `404 Not Found`; FastAPI has no matching route, so the event handler does not print the data. JavaScript shows its failure status and an error in Console. The Uvicorn access log shows a POST to `/event` with status 404.
</details>

## 4. Put the wrong Telegram token in `.env`

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

Browser-to-FastAPI succeeds, so Network shows a POST response from our backend, normally `502` after Telegram returns an unauthorized HTTP response. The page shows failure. The terminal prints Telegram's HTTP status (without printing the secret URL). Telegram sends no message. If the error is instead a Telegram JSON rejection with HTTP 200, the backend also returns `502` with the safe API-level message.
</details>

## 5. Remove CORS middleware

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

When the page is on a different origin, the browser may send an `OPTIONS` preflight. Without the CORS response headers, the browser blocks the JavaScript request and Console reports CORS. Network shows the preflight failure; often the POST is not sent. The FastAPI terminal may show the OPTIONS request but no event print. A direct curl/Postman request can still work because those clients do not enforce browser CORS.
</details>

## 6. Change JSON key `event_type` to `event` in JavaScript only

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

The browser sends a valid JSON object, but it is missing required `event_type`. Network shows `422`. Pydantic rejects it before the route's print. The frontend shows failure and logs the detail. If you are still in Chapter 2 with the plain `dict` version, it may instead accept the object; the result depends on which chapter's backend is running.
</details>

## 7. Stop Uvicorn and click a button

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

The browser cannot connect to FastAPI. Console reports a fetch/network error; Network shows a failed request without an HTTP status. No Uvicorn process exists to print the event or return a response.
</details>

## 8. Change only the frontend page port to 5501

**Predict first:** Console, Network, and terminal.

<details>
<summary>Answer — reveal after predicting</summary>

The origin changes because port is part of the origin. Since `http://localhost:5501` is not in `allow_origins`, the browser blocks the cross-origin call. Add that exact origin to allow the demo from that port. Uvicorn may log an OPTIONS preflight; the route will not print an event if the browser never sends the POST.
</details>

---

# Glossary

| Term | Meaning in this project |
|---|---|
| Frontend | The files delivered to the browser: `index.html`, `style.css`, and `script.js`. |
| Backend | The Python app in `backend/main.py`, run locally under Uvicorn. |
| Client | The program that starts a request. The browser calls FastAPI; `httpx` calls Telegram. |
| Server | The program waiting for a request. Uvicorn serves FastAPI; Telegram serves its Bot API. |
| HTTP | The rules both browser → FastAPI and FastAPI → Telegram use to exchange requests and responses. |
| API | A defined interface a program can call. Our `/event` endpoint and Telegram's Bot API are examples. |
| Endpoint | A callable method and path, such as `POST /event`. |
| Route | The FastAPI rule that connects an HTTP method and path to a Python function. |
| Request | A message from a client to a server, such as the browser's POST for a click. |
| Response | The server's answer, such as `200`, `422`, `503`, or `502` plus JSON. |
| Request body | Data attached to the request. The event JSON is the body of `POST /event`. |
| JSON | The text format used to carry `event_type`, `page`, `chat_id`, and `text`. |
| GET | A request method used here by the browser to ask for the health status. |
| POST | A request method used here to submit an event or ask Telegram to send a message. |
| Status code | The numeric response result. `200` is success; `422` is invalid request data; `503` is missing backend configuration; `502` means this backend could not complete its Telegram step. |
| CORS | Browser rules for reading cross-origin responses. It permits our local frontend origin; it does not authenticate requests. |
| Environment variable | A named setting read by the backend process, such as `TELEGRAM_CHAT_ID`. |
| Secret | Private data such as the Telegram bot token. Keep it in backend configuration, not frontend files or Git. |
| Token | Telegram's secret string that identifies the bot in Bot API requests. |
| Third-party API | An API run by an outside service; Telegram's Bot API is third-party to this project. |
| Async | A Python function style that can yield while waiting for network I/O. `send_telegram_message` is async. |
| Await | The expression that waits for an async operation's result, such as the `httpx` POST response. |
| Validation | Checking that incoming JSON has acceptable fields and values before the route runs. Pydantic performs it for `Event`. |
| Middleware | Code around route handling. `CORSMiddleware` adds browser CORS behavior before/after requests reach the route. |

---

## One last reminder

Do not optimize for giving me the answer quickly. Optimize for making me able to reproduce the answer after closing this chat.
