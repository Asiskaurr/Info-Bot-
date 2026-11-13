# InfoBot Frontend

Minimal browser-based chat interface for the InfoBot prototype. It sends questions to the local Flask API and displays the answer with any retrieved sources.

The microphone button uses the browser's built-in Web Speech API to transcribe a question into the message box. The user reviews the transcript and selects **Send**; the frontend sends only the recognized text to the existing API. No separate transcription API key or paid software is configured. Speech recognition support depends on the browser, so typing remains available as a fallback.

## Open the prototype

Start the Flask backend from the repository root with `python app.py`. In another terminal, serve the frontend with `python -m http.server 5500 --directory frontend`, then open `http://127.0.0.1:5500`. The backend's default CORS allowlist includes this origin.

To view the GTBIT-style demo page with the chatbot launcher, open `http://127.0.0.1:5500/demo.html`. The launcher opens the existing chatbot page in an iframe; the chat implementation remains in `index.html`.

## Configure the API address

The frontend sends requests to `API_URL` near the top of `app.js`, which defaults to `http://127.0.0.1:5000/api/chat`. Change it if the backend uses a different host or port.

When using a separate frontend and backend server, the backend must allow requests from the frontend's local origin (CORS), or serve the frontend from the same origin. Opening the page directly from disk works for mock mode.

## Chat API contract

The frontend sends a JSON request:

```http
POST /api/chat
Content-Type: application/json
```

```json
{
  "question": "Where can I find the CSE syllabus?"
}
```

The backend should return JSON in this shape:

```json
{
  "answer": "The CSE syllabus is available on the department's Academics page.",
  "sources": [
    {
      "title": "CSE Academics",
      "url": "https://www.gtbit.ac.in/academics",
      "snippet": "Syllabus and academic resources for the CSE department.",
      "source_number": 1,
      "page_number": 1
    }
  ]
}
```

Use an empty `sources` array when there are no citations. Each source may include `title`, `url`, `snippet`, `source_number`, and `page_number`; the frontend displays the title/link, citation number, and available details. The `answer` field must be a string. API errors use an `error` object with `code` and `message`; the chat displays the message for API errors and a connection hint if the backend cannot be reached.
