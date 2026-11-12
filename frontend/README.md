# InfoBot Frontend

Minimal browser-based chat interface for the InfoBot prototype. It currently uses a mock reply; no backend is required to view the page.

## Open the prototype

Open `index.html` in a browser. Type a question and select **Send** to see the mock answer and example source. The example source is a placeholder and was not retrieved in response to the question.

## Configure mock or API mode

In `app.js`, set `USE_MOCK_API` near the top:

- `true` keeps using the built-in mock response (current default).
- `false` sends a request to the URL in `API_URL`.

Update `API_URL` to the backend's local address when it is available. The current placeholder is `http://127.0.0.1:5000/api/chat`.

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
      "snippet": "Syllabus and academic resources for the CSE department."
    }
  ]
}
```

Use an empty `sources` array when there are no citations. Each source may include `title`, `url`, and `snippet`; the frontend displays the title/link and snippet when provided. The `answer` field must be a string. Error responses or failed connections currently display a generic connection message in the chat.
