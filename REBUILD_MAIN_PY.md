# Rebuild `main.py` Without Guessing

This tutorial rebuilds the backend in small working steps.

The goal is not to memorize the finished file. The goal is to understand each line well enough that you can delete `main.py` and recreate it.

The required path uses only Python, FastAPI, and FastAPI's `/docs` page until Telegram is introduced. JavaScript and CORS appear near the end and are optional while you learn the backend.

## The rule used in this tutorial

Each chapter teaches one new idea:

1. see the problem;
2. add the smallest code that solves it;
3. run the code;
4. observe one result;
5. answer one mental-check question.

When a chapter says **ADD**, **REPLACE**, or **DELETE**, make that change in `backend/main.py`. Complete versions of the file appear often so you can check that you did not keep an old version by accident.

This is an educational prototype. It does not add authentication, databases, rate limiting, Docker, queues, or production deployment.

---

# Chapter 0 — Set up the Python environment

## One new idea

Run installation commands and Uvicorn with the same Python environment.

## Why this matters

You can install FastAPI into one Python environment and accidentally run Uvicorn from another. Then this error appears even though you installed FastAPI:

```text
ModuleNotFoundError: No module named 'fastapi'
```

Using `python -m pip` and `python -m uvicorn` makes both commands use the `python` that is currently active.

## Windows PowerShell

Open a terminal in the backend folder:

```powershell
cd C:\Users\iix_m\Downloads\bot\backend
```

Create the environment once:

```powershell
python -m venv .venv
```

Activate it whenever you open a new terminal:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project packages:

```powershell
python -m pip install -r requirements.txt
```

Start the backend:

```powershell
python -m uvicorn main:app --reload
```

## macOS or Linux

From the `backend` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## What the command means

```text
python -m uvicorn main:app --reload
                  │    │
                  │    └── use the variable named app
                  └─────── import it from main.py
```

`--reload` restarts the development server after you save Python changes.

## Checkpoint

Your terminal should begin with `(.venv)` after activation. Uvicorn should say it is running at `http://127.0.0.1:8000`.

If Uvicorn says it cannot import `main`, check that the terminal is inside `backend`, where `main.py` exists.

## Mental check

Why do we use `python -m uvicorn` instead of relying on the command `uvicorn`?

<details>
<summary>Answer</summary>

It helps run Uvicorn with the same active Python environment used by `python -m pip`.
</details>

---

# Chapter 1 — Make one URL run one Python function

## One new idea

A request to a URL can make FastAPI call a Python function.

## Write the smallest app

**REPLACE** the contents of `backend/main.py` with:

<!-- checkpoint: chapter-1 -->

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

## Understand it in this order

When a browser asks for:

```text
GET /health
```

FastAPI calls:

```python
health()
```

The connection is created by this line:

```python
@app.get("/health")
```

Read it for now as:

> When a GET request arrives at `/health`, run the function below.

You do not need a deeper explanation of Python decorators yet.

The remaining lines mean:

- `from fastapi import FastAPI` — get the FastAPI class from the installed package.
- `app = FastAPI()` — create the application Uvicorn will run.
- `def health():` — define an ordinary Python function.
- `return {"status": "ok"}` — return a Python dictionary. FastAPI sends it as JSON.

## Run it

From `backend`, with the virtual environment active:

```powershell
python -m uvicorn main:app --reload
```

## Observe it

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Also open:

```text
http://127.0.0.1:8000/docs
```

FastAPI generated this page. When you click **Try it out** and **Execute**, `/docs` sends a real request to your backend.

## Small terms after seeing it work

- **GET** — the type of request. Here it asks for health information.
- **`/health`** — the path, meaning the part after `127.0.0.1:8000`.
- **response** — what the backend sends back.

## Checkpoint

Change `"ok"` to `"learning"`, save the file, and reload `/health`. Confirm the returned JSON changes. Then restore `"ok"`.

## Mental check

What Python function runs when `GET /health` arrives?

<details>
<summary>Answer</summary>

FastAPI calls `health()`.
</details>

---

# Chapter 2 — Give JSON data to a Python function

## One new idea

A POST request can carry JSON data into a Python function.

## Add the POST route

**ADD** this below `health()`:

```python
@app.post("/event")
def event(data: dict):
    print(data)
    return {"ok": True}
```

## Read the whole idea first

For now, read that code as:

> When you send JSON to `POST /event`, FastAPI gives that data to this Python function as `data`.

Do not separate every piece yet. First, see it happen.

## Your complete `main.py` now

<!-- checkpoint: chapter-2 -->

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

## Test it before learning more terms

1. Open `http://127.0.0.1:8000/docs`.
2. Open `POST /event`.
3. Click **Try it out**.
4. Put this into the request body:

   ```json
   {
     "event_type": "book_click"
   }
   ```

5. Click **Execute**.

Expected response in `/docs`:

```json
{"ok":true}
```

Expected output in the Uvicorn terminal:

```text
{'event_type': 'book_click'}
```

This is the important transformation:

```text
JSON sent through /docs
{"event_type":"book_click"}
              │
              ▼
Python value inside event()
data = {"event_type": "book_click"}
```

## Now separate the pieces

In this code:

```python
@app.post("/event")
def event(data: dict):
```

- `POST` is the request type.
- `/event` is the path we chose.
- `event` is the Python function name we chose.
- `data` is the parameter name we chose.
- `dict` means Python dictionary.
- `data: dict` tells FastAPI to expect a JSON object and give the function a dictionary.

The name `/event` is not connected to one button. It is only the path chosen for website events.

All of these can use the same route and the same function:

```json
{"event_type":"book_click"}
```

```json
{"event_type":"contact_click"}
```

```json
{"event_type":"page_visit"}
```

Send each one from `/docs`. The terminal prints a different dictionary each time, but FastAPI calls the same `event()` function.

## Connect it to Python you already know

FastAPI is doing work before it calls your function. The result is similar to these ordinary Python calls:

```python
event({"event_type": "book_click"})
event({"event_type": "contact_click"})
```

The real data arrives through HTTP instead of being typed directly into Python.

## Small error lesson: 404 and 405

Learn these only when you see them:

- `404 Not Found` — that path does not exist.
- `405 Method Not Allowed` — the path exists, but not for the request type you used.

For example, `GET /event` can produce 405 because we created `POST /event`, not `GET /event`.

## Checkpoint

Send this from `/docs`:

```json
{"event_type":"contact_click"}
```

Confirm the terminal prints a Python dictionary containing `contact_click`.

## Mental check

When you send `{"event_type":"book_click"}`, what is inside `data`?

<details>
<summary>Answer</summary>

Approximately this Python dictionary:

```python
{"event_type": "book_click"}
```
</details>

## Optional detail: does every button need another route?

No. In this project, several website actions will send different `event_type` values to the same `POST /event` route. Another API design could use `/book` and `/contact`, but that is not necessary for this notification demo.

---

# Chapter 3 — Describe which fields are expected with Pydantic

## One new idea

Pydantic checks that incoming data has the fields we expect.

## The server already works

This distinction is important:

> FastAPI already receives JSON with `data: dict`. Pydantic is not needed to make POST work.

The current route accepts any JSON object, including:

```json
{"event_type":"book_click"}
```

and:

```json
{"pizza":"banana"}
```

Both are dictionaries. We now want to describe what must be inside the dictionary.

We could write manual Python checks:

```python
if "event_type" not in data:
    return {"error": "event_type is missing"}
```

Pydantic saves us from writing these checks repeatedly and lets FastAPI return a useful error automatically.

## Add the model

**ADD** this import below the FastAPI import:

```python
from pydantic import BaseModel
```

**ADD** this class below `app = FastAPI()`:

```python
class Event(BaseModel):
    event_type: str
    page: str = "Hotel Demo"
```

**REPLACE**:

```python
def event(data: dict):
    print(data)
```

with:

```python
def event(data: Event):
    print(data)
```

## Your complete `main.py` now

<!-- checkpoint: chapter-3 -->

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Event(BaseModel):
    event_type: str
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def event(data: Event):
    print(data)
    return {"ok": True}
```

## Understand `str` immediately

`str` means string, which means text.

These are strings:

```text
"book_click"
"banana"
"hello"
```

Therefore:

```python
event_type: str
```

means:

> `event_type` must exist and its value must be text.

It does **not** mean that the value must be `"book_click"`.

This line:

```python
page: str = "Hotel Demo"
```

means `page` should be text. If it is missing, use `"Hotel Demo"`.

## Test three requests in `/docs`

### Test 1: expected field and text value

```json
{"event_type":"book_click"}
```

Expected: success. The terminal prints approximately:

```text
event_type='book_click' page='Hotel Demo'
```

### Test 2: wrong field name

```json
{"pizza":"banana"}
```

Expected: `422 Unprocessable Entity`.

Why it fails:

```text
Does event_type exist?  No
```

### Test 3: expected field with another text value

```json
{"event_type":"banana"}
```

Expected: success.

Why it passes:

```text
Does event_type exist?  Yes
Is "banana" text?       Yes
```

Pydantic currently checks approximately:

```text
Does event_type exist?
Is its value text?
```

We have not told it which text values are allowed yet.

## Dictionary before, Event object after

Before Pydantic:

```python
data["event_type"]
```

After Pydantic:

```python
data.event_type
data.page
```

FastAPI reads the JSON, Pydantic checks it, and the function receives an `Event` object.

## Checkpoint

Make sure your route now says:

```python
def event(data: Event):
```

If it still says `data: dict`, you have not applied this chapter's change.

## Mental check

Why does `{"pizza":"banana"}` fail while `{"event_type":"banana"}` passes?

<details>
<summary>Answer</summary>

The first object is missing the required field named `event_type`. The second has `event_type`, and `"banana"` is text, so it satisfies `event_type: str`.
</details>

## Optional detail: extra fields

In this basic Pydantic model, unexpected extra fields are ignored by default. We do not need to change that behavior for this tutorial.

---

# Chapter 4 — Allow only our real event names

## One new idea

`Literal` restricts text to a small list of exact values.

## The problem

This still passes:

```json
{"event_type":"banana"}
```

It passes because `"banana"` is text. We want only the three event names used by this project.

## Make one field stricter

**ADD** this import at the top:

```python
from typing import Literal
```

**REPLACE**:

```python
event_type: str
```

with:

```python
event_type: Literal[
    "page_visit",
    "book_click",
    "contact_click",
]
```

Read the change like this:

```text
str
→ any text

Literal[...]
→ only these exact values
```

## Your complete `main.py` now

<!-- checkpoint: chapter-4 -->

```python
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Event(BaseModel):
    event_type: Literal[
        "page_visit",
        "book_click",
        "contact_click",
    ]
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def event(data: Event):
    print(data)
    return {"ok": True}
```

## Test it

Send:

```json
{"event_type":"book_click"}
```

Expected: success.

Then send:

```json
{"event_type":"banana"}
```

Expected: `422 Unprocessable Entity`.

The route function does not run for the invalid request because FastAPI and Pydantic reject it before calling `event()`.

## Checkpoint

Look at the Uvicorn terminal. The valid event should be printed; `banana` should not be printed by your `print(data)` line.

## Mental check

Why did `banana` pass in Chapter 3 but fail now?

<details>
<summary>Answer</summary>

`str` allowed any text. `Literal[...]` allows only the exact event names listed in the model.
</details>

---

# Chapter 5 — Turn an Event into message text

## One new idea

A normal Python function can receive the validated Event and return a message string.

## Start with the readable version

Do not optimize the repeated `if` statements yet.

**ADD** this function above the POST route:

```python
def make_message(event):
    if event.event_type == "book_click":
        return "🔔 Book Now Clicked"

    if event.event_type == "contact_click":
        return "📩 Contact Button Clicked"

    if event.event_type == "page_visit":
        return "🌐 Page Visit"
```

**REPLACE** the body of the POST route with:

```python
@app.post("/event")
def event(data: Event):
    message = make_message(data)
    print(message)
    return {"ok": True}
```

## Understand the flow with ordinary Python

```text
data is an Event object
        │
        ▼
make_message(data)
        │
        ▼
returns a Python string
        │
        ▼
message stores that string
```

This is similar to an ordinary Python call:

```python
message = make_message(data)
```

FastAPI is not doing anything special inside `make_message`. It is a normal function.

We intentionally write `def make_message(event):` without parameter or return annotations. First understand input → function → returned string. An optional note later adds annotations.

## Your complete `main.py` now

<!-- checkpoint: chapter-5 -->

```python
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Event(BaseModel):
    event_type: Literal[
        "page_visit",
        "book_click",
        "contact_click",
    ]
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


def make_message(event):
    if event.event_type == "book_click":
        return "🔔 Book Now Clicked"

    if event.event_type == "contact_click":
        return "📩 Contact Button Clicked"

    if event.event_type == "page_visit":
        return "🌐 Page Visit"


@app.post("/event")
def event(data: Event):
    message = make_message(data)
    print(message)
    return {"ok": True}
```

## Test it

Send from `/docs`:

```json
{"event_type":"book_click"}
```

Expected terminal output:

```text
🔔 Book Now Clicked
```

Send `contact_click` and `page_visit` too. Each value should print the matching string.

## Why no final `else` is required here

`Literal` already rejected every other event name before `make_message()` was called. Therefore one of the three `if` statements will match.

## Checkpoint

Do not continue until all three valid event names print the expected message.

## Mental check

If `event.event_type` is `"contact_click"`, what does `make_message(event)` return?

<details>
<summary>Answer</summary>

The string `"📩 Contact Button Clicked"`.
</details>

## Optional refactor — later, not required

The three `if` statements could eventually be replaced with a dictionary lookup. That version is shorter, but it combines dictionary values and lookup into the lesson. Keep the `if` version until the behavior feels obvious.

## Optional type annotations

After you understand the function, you may describe its input and output:

```python
def make_message(event: Event) -> str:
```

`event: Event` says the expected input is an Event object. `-> str` says the function returns text. These annotations do not change the message logic.

---

# Chapter 6 — Include the page in the message

## One new idea

Use another validated field when building the returned string.

## Change only `make_message()`

**REPLACE** the function with:

```python
def make_message(event):
    if event.event_type == "book_click":
        icon = "🔔"
        event_text = "Book Now Clicked"

    if event.event_type == "contact_click":
        icon = "📩"
        event_text = "Contact Button Clicked"

    if event.event_type == "page_visit":
        icon = "🌐"
        event_text = "Page Visit"

    message = (
        f"{icon} Website Event\n\n"
        f"Event: {event_text}\n"
        f"Page: {event.page}"
    )
    return message
```

## What changed

Previously, each `if` returned immediately. Now each matching `if` stores an icon and readable event text. After the checks, one return statement builds the complete message.

This line is an f-string:

```python
message = (
    f"{icon} Website Event\n\n"
    f"Event: {event_text}\n"
    f"Page: {event.page}"
)
```

- `{icon}` and `{event_text}` insert the selected values.
- `\n` starts a new line.
- `{event.page}` inserts the page field.

## Test it

Send:

```json
{
  "event_type": "book_click",
  "page": "Room 204"
}
```

Expected terminal output:

```text
🔔 Website Event

Event: Book Now Clicked
Page: Room 204
```

Then leave out `page`:

```json
{"event_type":"book_click"}
```

Expected page line:

```text
Page: Hotel Demo
```

That value comes from the model default:

```python
page: str = "Hotel Demo"
```

## Mental check

Where does `event.page` come from when the request body does not include `page`?

<details>
<summary>Answer</summary>

Pydantic uses the default value `"Hotel Demo"` defined in the Event model.
</details>

---

# Chapter 7 — Add a backend timestamp

## One new idea

The backend creates the event time instead of trusting a time sent by the caller.

## Add the datetime import

**ADD** at the top:

```python
from datetime import datetime, timezone
```

## Change the end of `make_message()`

**REPLACE**:

```python
message = (
    f"{icon} Website Event\n\n"
    f"Event: {event_text}\n"
    f"Page: {event.page}"
)
return message
```

with:

```python
timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

message = (
    f"{icon} Website Event\n\n"
    f"Event: {event_text}\n"
    f"Page: {event.page}\n"
    f"Time: {timestamp}"
)
return message
```

## Read the new line

```python
datetime.now(timezone.utc)
```

gets the current time in UTC.

```python
.isoformat(timespec="seconds")
```

turns that time into readable text and keeps seconds instead of smaller fractions.

The parentheses let us write one long string across several code lines. The adjacent f-strings join into one string.

## Your complete `main.py` now

<!-- checkpoint: chapter-7 -->

```python
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Event(BaseModel):
    event_type: Literal[
        "page_visit",
        "book_click",
        "contact_click",
    ]
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


def make_message(event):
    if event.event_type == "book_click":
        icon = "🔔"
        event_text = "Book Now Clicked"

    if event.event_type == "contact_click":
        icon = "📩"
        event_text = "Contact Button Clicked"

    if event.event_type == "page_visit":
        icon = "🌐"
        event_text = "Page Visit"

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    message = (
        f"{icon} Website Event\n\n"
        f"Event: {event_text}\n"
        f"Page: {event.page}\n"
        f"Time: {timestamp}"
    )
    return message


@app.post("/event")
def event(data: Event):
    message = make_message(data)
    print(message)
    return {"ok": True}
```

## Test it

Send a valid event from `/docs`. The terminal should show three lines: event text, page, and a UTC time.

## Mental check

Why create the timestamp in Python instead of accepting a timestamp from the browser?

<details>
<summary>Answer</summary>

The backend records when it processed the event. A caller could send an incorrect or invented time.
</details>

---

# Chapter 8 — Understand the Telegram request before coding it

## One new idea

Our backend can send a second HTTP request to Telegram.

## The two requests

```text
/docs sends an event
        │
        ▼
FastAPI receives POST /event
        │
        ▼
Python builds message text
        │
        ▼
Python sends POST /sendMessage to Telegram
```

For the first request, our backend receives data. For the second request, our backend sends data to another API.

More precisely, `httpx` will be the Python library that sends the Telegram request.

## What Telegram needs

Conceptually, the request looks like:

```text
POST https://api.telegram.org/bot<TOKEN>/sendMessage
```

JSON body:

```json
{
  "chat_id": "<CHAT_ID>",
  "text": "🔔 Book Now Clicked"
}
```

- the token identifies your bot;
- `chat_id` identifies the destination chat;
- `text` is the message.

There is no code change in this chapter. Its purpose is to understand the next network step before adding Python syntax.

## Mental check

What library will make the outgoing Telegram request?

<details>
<summary>Answer</summary>

`httpx`.
</details>

---

# Chapter 9 — Keep the token outside Python code

## One new idea

Read private configuration from environment variables instead of writing credentials in source code.

## Why add this before the real request?

The Telegram request needs a token. Putting a real token in `main.py` makes it easy to commit or share accidentally. Putting it in frontend JavaScript would also expose it to visitors.

The project already has:

```text
backend/.env
```

This is a plain text file stored locally. Git ignores it.

It should contain:

```env
TELEGRAM_BOT_TOKEN=your_real_token_here
TELEGRAM_CHAT_ID=your_real_chat_id_here
```

Never copy real values into this tutorial, `main.py`, or Git.

## Add the imports

**ADD**:

```python
import os
from dotenv import load_dotenv
```

## Load the file

**ADD** this after all imports:

```python
load_dotenv()
```

## Read the values

For now, add these two lines below `load_dotenv()` so you can understand them:

```python
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
```

- `load_dotenv()` reads `.env` into this Python process.
- `os.getenv(...)` gets one named value.
- If the name does not exist, `os.getenv(...)` returns `None`.

We will move these two reads into the Telegram function in the next chapter.

## Observe without printing the secret

Do not print `token`.

You may temporarily check whether both values exist:

```python
print(token is not None)
print(chat_id is not None)
```

The output should be `True` for each configured value. Delete these two print lines afterward.

## Mental check

Does `.env` get sent to the browser?

<details>
<summary>Answer</summary>

No. `load_dotenv()` reads it inside the backend Python process. The backend must also avoid returning or printing the token.
</details>

---

# Chapter 10 — Send the message with `httpx`

## One new idea

Use an HTTP client to send the message, then wait for Telegram's response.

## Add the HTTP client import

**ADD**:

```python
import httpx
```

## Remove the temporary top-level credential reads

If Chapter 9 still has these lines directly below `load_dotenv()`, **DELETE** them:

```python
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
```

The new function will read them when it sends a message.

## Add the sending function

**ADD** this below `make_message()`:

```python
async def send_message_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_data = {
        "chat_id": chat_id,
        "text": message,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=telegram_data)

    print(response.status_code)
    print(response.text)
```

## Change the event route

The old route is a normal function:

```python
@app.post("/event")
def event(data: Event):
    message = make_message(data)
    print(message)
    return {"ok": True}
```

**REPLACE** it with:

```python
@app.post("/event")
async def event(data: Event):
    message = make_message(data)
    await send_message_to_telegram(message)
    return {"ok": True}
```

## Understand why `async` appears now

Before this chapter, the route only ran local Python code. Now it waits for another server over the internet:

```text
FastAPI receives /event
        │
        ▼
httpx sends the Telegram request
        │
        ▼
the network response may take time
```

`async def` allows this function to use `await`.

`await` means:

> Wait here for Telegram's response before continuing this function.

It does not mean “run in the background.” While this code waits on network input/output, Python's event loop can work on other tasks. You do not need event-loop details to continue.

`async with` opens the HTTP client and closes its network resources after the indented block.

## Your complete `main.py` now

<!-- checkpoint: chapter-10 -->

```python
import os
from datetime import datetime, timezone
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

app = FastAPI()


class Event(BaseModel):
    event_type: Literal[
        "page_visit",
        "book_click",
        "contact_click",
    ]
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


def make_message(event):
    if event.event_type == "book_click":
        icon = "🔔"
        event_text = "Book Now Clicked"

    if event.event_type == "contact_click":
        icon = "📩"
        event_text = "Contact Button Clicked"

    if event.event_type == "page_visit":
        icon = "🌐"
        event_text = "Page Visit"

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    message = (
        f"{icon} Website Event\n\n"
        f"Event: {event_text}\n"
        f"Page: {event.page}\n"
        f"Time: {timestamp}"
    )
    return message


async def send_message_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_data = {
        "chat_id": chat_id,
        "text": message,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=telegram_data)

    print(response.status_code)
    print(response.text)


@app.post("/event")
async def event(data: Event):
    message = make_message(data)
    await send_message_to_telegram(message)
    return {"ok": True}
```

## Test it

Restart Uvicorn after changing `.env`. Send a valid event from `/docs`.

With valid credentials, Telegram should return status `200` and send the message. If the credentials are missing or wrong, this basic version may print a Telegram error. The next chapters make those errors readable.

Do not treat `{"ok":true}` from our route as proof of Telegram success yet. We have not checked Telegram's response before returning it.

## Mental check

Why did the event route change from `def` to `async def` in this chapter?

<details>
<summary>Answer</summary>

It now calls an async HTTP function with `await` while waiting for Telegram's network response.
</details>

---

# Chapter 11 — Stop early when credentials are missing

## One new idea

Return a clear HTTP error instead of building a Telegram URL with missing values.

## Add `HTTPException`

**REPLACE**:

```python
from fastapi import FastAPI
```

with:

```python
from fastapi import FastAPI, HTTPException
```

## Add the check

Inside `send_message_to_telegram()`, after reading `token` and `chat_id`, **ADD**:

```python
if not token or not chat_id:
    raise HTTPException(
        status_code=503,
        detail="Telegram is not configured. Check backend/.env.",
    )
```

Read it as:

> If either value is missing, stop this request and return a 503 response with a safe explanation.

We use `503` here because the endpoint cannot complete its Telegram work while required backend configuration is unavailable.

## Test it

Temporarily rename `backend/.env`, restart Uvicorn, and send a valid event.

Expected `/docs` response status:

```text
503 Service Unavailable
```

Expected response body:

```json
{"detail":"Telegram is not configured. Check backend/.env."}
```

Restore `.env` and restart Uvicorn afterward.

## Mental check

Does Pydantic detect the missing Telegram token?

<details>
<summary>Answer</summary>

No. Pydantic checks incoming event data. This `if` statement checks backend configuration.
</details>

---

# Chapter 12 — Handle Telegram failures

## One new idea

Different failures happen in different places. Handle the two Telegram-request failures we care about.

## First add status checking

After the `async with` block, **ADD**:

```python
response.raise_for_status()
```

This tells `httpx` to raise an error when Telegram responds with a failing HTTP status such as `401 Unauthorized`.

## Then add focused error handling

**REPLACE** the HTTP section inside `send_message_to_telegram()` with:

```python
try:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=telegram_data)

    response.raise_for_status()

    telegram_result = response.json()
    if not telegram_result.get("ok"):
        raise HTTPException(
            status_code=502,
            detail="Telegram did not accept the message.",
        )

except httpx.HTTPStatusError as error:
    print(f"Telegram returned HTTP {error.response.status_code}.")
    raise HTTPException(
        status_code=502,
        detail="Telegram rejected the message. Check the bot settings.",
    ) from None

except httpx.RequestError as error:
    print(f"Could not reach Telegram: {error}")
    raise HTTPException(
        status_code=502,
        detail="Could not reach Telegram.",
    ) from None
```

There are two cases:

- `HTTPStatusError` — Telegram answered, but rejected the request.
- `RequestError` — the HTTP request could not complete, for example because of a connection or timeout problem.

After a successful HTTP status, `response.json()` reads Telegram's JSON result. Its `ok` value tells us whether Telegram accepted the Bot API operation. This is a Telegram-specific check; `raise_for_status()` checks only the HTTP status.

`timeout=10.0` prevents this learning app from waiting forever.

## Small debugging table

| What you see | Likely layer |
|---|---|
| `422` | Event data failed Pydantic validation. |
| `503` | Telegram configuration is missing. |
| `502` with “rejected” | Telegram answered with an error. |
| `502` with “could not reach” | Network request to Telegram failed. |
| Browser says connection refused | Uvicorn is probably not running at that address. |

## Mental check

What is the difference between `HTTPStatusError` and `RequestError` here?

<details>
<summary>Answer</summary>

`HTTPStatusError` means Telegram sent an HTTP error response. `RequestError` means the network request itself could not complete.
</details>

---

# Chapter 13 — Optional: connect the browser frontend and CORS

> You may skip this chapter while learning the backend. `/docs` remains a complete testing client for every required backend chapter.

## One new idea

A browser page can send the same `POST /event` request that `/docs` sends.

FastAPI does not care whether the HTTP request came from `/docs`, Postman, JavaScript, a mobile app, or another Python program.

```text
Today:
/docs → POST /event → FastAPI

Later:
browser JavaScript → POST /event → FastAPI
```

## Why JavaScript is needed for this page

An ordinary HTML `<form>` normally sends form-encoded data. Our FastAPI endpoint expects a JSON object. The existing `frontend/script.js` uses `fetch()` to send JSON.

You do not need to understand its JavaScript syntax to finish the backend tutorial.

## Why CORS appears now

The local frontend and backend use different addresses:

```text
frontend: http://localhost:5500
backend:  http://127.0.0.1:8000
```

A browser treats these as different origins. An origin is the scheme, host, and port together. The browser needs the backend response to say that this local frontend origin is allowed.

## Add the CORS import

**ADD**:

```python
from fastapi.middleware.cors import CORSMiddleware
```

## Add the middleware after `app = FastAPI()`

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

- `allow_origins` lists the local frontend addresses.
- `allow_methods` allows its GET and POST requests.
- `allow_headers` allows the JSON content-type header.

CORS is a browser rule. It is not authentication. Allowing an origin does not stop curl, Postman, another server, or another script from calling a public API.

## Correct meaning of a relative URL

If the frontend page at `http://localhost:5500` used:

```javascript
fetch("/event")
```

the browser would normally target:

```text
http://localhost:5500/event
```

Our backend is at `http://127.0.0.1:8000`, so the existing frontend uses the full backend URL.

## Run the optional frontend

In a second terminal:

```powershell
cd C:\Users\iix_m\Downloads\bot\frontend
python -m http.server 5500
```

Open `http://localhost:5500`.

The `favicon.ico` 404 from the simple file server is harmless.

## Mental check

Does CORS stop Postman from calling the API?

<details>
<summary>Answer</summary>

No. CORS is enforced by browsers. It is not backend authentication or permission checking.
</details>

## Optional security note for later

Hiding a button is not permission control. A public backend would need to enforce permissions itself. Validation, authentication, and rate limiting solve different problems. Those topics are deliberately outside this first backend tutorial.

---

# Chapter 14 — Complete final `main.py`

## One new idea

No new idea. This chapter assembles the code you already built.

Compare your file carefully. Do not paste the final version before understanding the earlier checkpoints.

<!-- checkpoint: chapter-14 -->

```python
import os
from datetime import datetime, timezone
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

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
    event_type: Literal[
        "page_visit",
        "book_click",
        "contact_click",
    ]
    page: str = "Hotel Demo"


@app.get("/health")
def health():
    return {"status": "ok"}


def make_message(event):
    if event.event_type == "book_click":
        icon = "🔔"
        event_text = "Book Now Clicked"

    if event.event_type == "contact_click":
        icon = "📩"
        event_text = "Contact Button Clicked"

    if event.event_type == "page_visit":
        icon = "🌐"
        event_text = "Page Visit"

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    message = (
        f"{icon} Website Event\n\n"
        f"Event: {event_text}\n"
        f"Page: {event.page}\n"
        f"Time: {timestamp}"
    )
    return message


async def send_message_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise HTTPException(
            status_code=503,
            detail="Telegram is not configured. Check backend/.env.",
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_data = {
        "chat_id": chat_id,
        "text": message,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=telegram_data)

        response.raise_for_status()

        telegram_result = response.json()
        if not telegram_result.get("ok"):
            raise HTTPException(
                status_code=502,
                detail="Telegram did not accept the message.",
            )

    except httpx.HTTPStatusError as error:
        print(f"Telegram returned HTTP {error.response.status_code}.")
        raise HTTPException(
            status_code=502,
            detail="Telegram rejected the message. Check the bot settings.",
        ) from None

    except httpx.RequestError as error:
        print(f"Could not reach Telegram: {error}")
        raise HTTPException(
            status_code=502,
            detail="Could not reach Telegram.",
        ) from None


@app.post("/event")
async def event(data: Event):
    print(f"Received event: {data.model_dump()}")
    message = make_message(data)
    await send_message_to_telegram(message)
    return {"success": True, "event_type": data.event_type}
```

## Final request flow

```text
/docs or browser
    │ sends JSON to POST /event
    ▼
FastAPI
    │ gives JSON to Pydantic
    ▼
Event object
    │ goes to make_message()
    ▼
message string
    │ goes to httpx
    ▼
Telegram Bot API
    │ responds to the backend
    ▼
backend responds to the original caller
```

## Final mental check

Explain these lines in your own words:

```text
data: dict
Event(BaseModel)
event_type: str
Literal[...]
make_message(event)
await send_message_to_telegram(message)
```

Suggested answer:

```text
data: dict
→ accept a dictionary.

Event(BaseModel)
→ describe and validate the fields expected in incoming data.

event_type: str
→ event_type must exist and contain text.

Literal[...]
→ only the listed event names are allowed.

make_message(event)
→ turn the validated Event object into message text.

await send_message_to_telegram(message)
→ wait while httpx sends that text to Telegram.
```

---

# Rebuild It Without Looking

Try each step from memory. Run the app after each important step.

1. Create the FastAPI app.
2. Add `GET /health`.
3. Add `POST /event` with `data: dict`.
4. Send `book_click` through `/docs` and observe the dictionary.
5. Add the Pydantic Event model.
6. Explain why `pizza` as a key fails but `banana` as `event_type` passes.
7. Restrict `event_type` with `Literal`.
8. Write `make_message(event)` with readable `if` statements.
9. Add page and backend time to the string.
10. Read Telegram settings from `.env`.
11. Send the Telegram request with `httpx`.
12. Add missing-configuration and Telegram error handling.
13. Add CORS when you are ready to connect the browser frontend.

---

# Break-It Exercises

Predict the result before trying each exercise. Use `/docs` unless the exercise specifically mentions the browser frontend.

## 1. Change the path to `/events`

Change only the backend decorator from `/event` to `/events`, then send `POST /event`.

<details>
<summary>Answer</summary>

`POST /event` returns 404 because that path no longer exists. `/docs` shows `POST /events`.
</details>

## 2. Change POST to GET

Change only `@app.post("/event")` to `@app.get("/event")`.

<details>
<summary>Answer</summary>

A POST request to `/event` returns 405 because the path exists for GET but not POST. `/docs` shows the event operation under GET.
</details>

## 3. Rename the Python function

Keep the decorator unchanged but rename:

```python
def event(data: Event):
```

to:

```python
def banana(data: Event):
```

<details>
<summary>Answer</summary>

`POST /event` still works. The decorator controls the request method and path; the function name is a Python name.
</details>

## 4. Send a different body to the same route

With the Chapter 2 version, send `book_click`, then `contact_click` to `POST /event`.

<details>
<summary>Answer</summary>

The same function runs twice. The value inside `data` changes.
</details>

## 5. Send the wrong field name after adding Pydantic

Send:

```json
{"event":"book_click"}
```

<details>
<summary>Answer</summary>

The response is 422 because required field `event_type` is missing. The route function does not run.
</details>

## 6. Remove `book_click` from Literal

Then send `book_click`.

<details>
<summary>Answer</summary>

Pydantic rejects it with 422 because it is no longer one of the allowed exact values.
</details>

## 7. Stop Uvicorn

Try `/docs` after stopping the server.

<details>
<summary>Answer</summary>

The browser cannot connect because no process is listening at port 8000. There is no HTTP status response from FastAPI.
</details>

## 8. Use the wrong Telegram token

Change the token locally, restart Uvicorn, and send a valid event. Restore the real setting afterward.

<details>
<summary>Answer</summary>

Telegram answers with an error status. `response.raise_for_status()` creates `HTTPStatusError`, and our backend returns 502 with the safe “Telegram rejected” detail.
</details>

## 9. Remove CORS and use the browser frontend

This exercise requires the optional frontend.

<details>
<summary>Answer</summary>

The browser blocks the cross-origin JavaScript request or response. `/docs` and Postman can still call the API because browser CORS rules do not apply to them.
</details>

---

# Small glossary

- **client** — a program that starts an HTTP request. `/docs`, Postman, and the browser can be clients.
- **server** — a program listening for requests. Uvicorn runs our FastAPI application locally.
- **request** — data sent from a client to a server.
- **response** — what the server sends back.
- **GET** — a request type commonly used to ask for data.
- **POST** — a request type commonly used to submit data for processing.
- **path** — the URL part such as `/health` or `/event`.
- **request body** — the data carried by a request. This project uses JSON bodies.
- **JSON** — the text format used to send objects such as `{"event_type":"book_click"}`.
- **validation** — checking that incoming data has the expected fields and values.
- **environment variable** — a named value available to the backend process.
- **CORS** — a browser rule for cross-origin requests; it is not authentication.
- **async** — allows a function to use `await` for asynchronous work such as network I/O.
- **await** — wait at this point for an async operation to finish; it does not mean “background.”

---

# Official references used for the technical baseline

- [FastAPI: First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI: Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic: Models](https://docs.pydantic.dev/latest/concepts/models/)
- [HTTPX: Async Support](https://www.python-httpx.org/async/)
- [Uvicorn: Settings](https://www.uvicorn.org/settings/)

Do not optimize for getting to the final answer quickly. Optimize for being able to reproduce it after closing this tutorial.
