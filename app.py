from flask import Flask, request, jsonify
from rag.rag_system import answer_question

app = Flask(__name__)

# Development CORS configuration.
# Restrict this to your frontend origin before production deployment.
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "GTBIT chatbot backend is running."
    }), 200


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():

    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(silent=True)

        if not data or not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request. JSON body required."
            }), 400

        question = data.get("question")

        if not isinstance(question, str) or not question.strip():
            return jsonify({
                "error": "Please provide a valid question."
            }), 400

        # Run the RAG pipeline
        result = answer_question(question.strip())

        # Format sources for the frontend
        formatted_sources = []
        seen_urls = set()

        for source in result.get("sources", []):

            url = source.get("source_url", "").strip()

            # Only return usable public URLs
            if not url.startswith(("http://", "https://")):
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            formatted_sources.append({
                "title": source.get("title") or "GTBIT Resource",
                "url": url
            })

        return jsonify({
            "answer": result.get("answer", ""),
            "sources": formatted_sources
        }), 200

    except Exception as error:

        app.logger.exception("Chat endpoint failed")

        return jsonify({
            "error": "Unable to process your question right now.",
            "details": str(error)
        }), 500


if __name__ == "__main__":
    print("Starting GTBIT Chatbot Backend...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )