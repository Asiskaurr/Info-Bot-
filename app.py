import os
from urllib.parse import urlsplit

from flask import Flask, jsonify, request
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)

DEFAULT_FRONTEND_ORIGINS = {
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


def get_allowed_origins():
    configured = os.getenv("FRONTEND_ORIGINS")
    if configured is None:
        return DEFAULT_FRONTEND_ORIGINS
    return {origin.strip() for origin in configured.split(",") if origin.strip()}


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and origin in get_allowed_origins():
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def api_error(code, message, status):
    return jsonify({"error": {"code": code, "message": message}}), status


@app.route("/health", methods=["GET"])
def health():
    """Liveness check; does not load models or require the data files."""
    return jsonify({
        "status": "success",
        "message": "GTBIT chatbot backend is running.",
    }), 200


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness check for credentials and a non-empty Chroma collection."""
    try:
        from rag.rag_system import check_readiness

        is_ready, message = check_readiness()
    except Exception:
        app.logger.exception("Readiness check failed")
        return api_error(
            "BACKEND_NOT_READY",
            "The chatbot backend is not ready. Check its configuration and knowledge base.",
            503,
        )

    if not is_ready:
        return api_error("BACKEND_NOT_READY", message, 503)

    return jsonify({"status": "success", "message": message}), 200


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error(
            "INVALID_JSON",
            "Send a JSON object containing a question.",
            400,
        )

    question = data.get("question")
    if not isinstance(question, str) or not question.strip():
        return api_error(
            "EMPTY_QUESTION",
            "Enter a question before sending.",
            400,
        )

    try:
        # Lazy import lets /health work even before the local RAG assets exist.
        from rag.rag_system import BackendNotReady, answer_question

        result = answer_question(question.strip())
    except BackendNotReady as error:
        app.logger.warning("Chat backend is not ready: %s", error)
        return api_error("BACKEND_NOT_READY", str(error), 503)
    except RuntimeError:
        app.logger.exception("Answer generation failed")
        return api_error(
            "ANSWER_GENERATION_FAILED",
            "InfoBot could not generate an answer right now. Please try again.",
            502,
        )
    except Exception:
        app.logger.exception("Chat endpoint failed")
        return api_error(
            "INTERNAL_ERROR",
            "InfoBot could not process your question right now.",
            500,
        )

    answer = result.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        app.logger.error("RAG pipeline returned an empty or invalid answer")
        return api_error(
            "INVALID_BACKEND_RESPONSE",
            "InfoBot could not produce an answer right now.",
            502,
        )

    # Keep the public response small and aligned with the frontend contract.
    formatted_sources = []
    for source in result.get("sources", []):
        if not isinstance(source, dict):
            continue

        url = str(source.get("source_url") or "").strip()
        try:
            parsed_url = urlsplit(url)
        except ValueError:
            continue
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            continue

        item = {
            "title": str(source.get("title") or "GTBIT Resource"),
            "url": url,
            "snippet": str(source.get("snippet") or ""),
        }
        source_number = source.get("source_number")
        if source_number not in (None, ""):
            item["source_number"] = source_number
        page_number = source.get("page_number")
        if page_number not in (None, ""):
            item["page_number"] = page_number
        formatted_sources.append(item)

    return jsonify({
        "answer": answer.strip(),
        "sources": formatted_sources,
    }), 200


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    print(f"Starting GTBIT chatbot backend at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
