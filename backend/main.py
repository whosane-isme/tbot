import os
from datetime import datetime, timezone
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Read backend/.env values into this process. The browser never sees them.
load_dotenv()

app = FastAPI()

# This is intentionally limited to local development addresses for the demo page.
# CORS lets a page on port 5500 call the API on port 8000; it is not access control.
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
    # FastAPI parses the incoming JSON body and Pydantic checks this event name.
    event_type: Literal["page_visit", "book_click", "contact_click"]
    page: str = "Hotel Demo"


@app.get("/health")
async def health():
    # A small route you can open in a browser to confirm the server is running.
    return {"status": "ok"}


def make_telegram_message(event: Event) -> str:
    """Turn one validated event into a readable message with a backend timestamp."""
    messages = {
        "page_visit": ("🌐 Website Event", "Page Visit"),
        "book_click": ("🔔 Website Event", "Book Now Clicked"),
        "contact_click": ("📩 Website Event", "Contact Button Clicked"),
    }
    icon_and_title = messages[event.event_type]
    # Generate time on the backend; Z means UTC.
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return (
        f"{icon_and_title[0]}\n\n"
        f"Event: {icon_and_title[1]}\n"
        f"Page: {event.page}\n"
        f"Time: {timestamp}"
    )


async def send_telegram_message(message: str) -> None:
    # These secrets stay in the backend environment, never in script.js or HTML.
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise HTTPException(
            status_code=503,
            detail="Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in backend/.env.",
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # httpx makes the backend's HTTP request to Telegram. await lets FastAPI handle
    # other requests while this network request is waiting for a response.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": message})
        response.raise_for_status()
        telegram_result = response.json()
        if not telegram_result.get("ok"):
            raise HTTPException(status_code=502, detail="Telegram did not accept the message.")
    except httpx.HTTPStatusError as error:
        # Do not return Telegram's full response or the secret URL to the browser.
        print(f"Telegram returned HTTP {error.response.status_code}.")
        raise HTTPException(status_code=502, detail="Telegram rejected the message. Check your bot settings.") from None
    except httpx.RequestError as error:
        print(f"Could not reach Telegram: {error}")
        raise HTTPException(status_code=502, detail="Could not reach Telegram. Check your internet connection.") from None


@app.post("/event")
async def receive_event(event: Event):
    # POST carries the event JSON in its request body. FastAPI validates it as Event.
    print(f"Received event: {event.model_dump()}")
    message = make_telegram_message(event)
    await send_telegram_message(message)
    return {"success": True, "event_type": event.event_type}
