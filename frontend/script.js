// FastAPI runs separately from this page. Keep the Telegram bot token out of
// frontend files: anything shipped to a browser can be inspected by visitors.
const API_URL = "http://127.0.0.1:8000";
const statusMessage = document.querySelector("#status");

async function sendEvent(eventType) {
  statusMessage.textContent = "Sending event…";

  try {
    // fetch sends an HTTP POST to our backend. JSON.stringify turns this object
    // into JSON text for the request body; the backend parses and validates it.
    const response = await fetch(`${API_URL}/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: eventType, page: "Hotel Demo" }),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || `Request failed (${response.status})`);
    }
    statusMessage.textContent = "Event sent successfully.";
  } catch (error) {
    // A useful console message helps distinguish a network problem from a click issue.
    console.error("Could not send event to FastAPI:", error);
    statusMessage.textContent = "Failed to send event. Check the browser console.";
  }
}

document.querySelector("#book-button").addEventListener("click", () => {
  sendEvent("book_click");
});

document.querySelector("#contact-button").addEventListener("click", () => {
  sendEvent("contact_click");
});

// Send this once when the page loads. Reloading the page sends another event.
sendEvent("page_visit");
