# 🤖 Info-Bot
### AI-Powered College Information Assistant

<p align="center">
  An intelligent chatbot designed to make institutional information accessible through natural language conversations.
</p>

<p align="center">
  <b>Python</b> · <b>Flask</b> · <b>Google Gemini</b> · <b>ChromaDB</b> · <b>Sentence Transformers</b>
</p>

---

## 📌 Overview

**Info-Bot** is an AI-powered information chatbot developed for **Guru Tegh Bahadur Institute of Technology (GTBIT)**.

The system enables students to access college-related information by asking questions in natural language, eliminating the need to manually search through multiple webpages and PDF documents.

It uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from institutional data and generate context-aware responses using Google's Gemini language model.

The project aims to make college information retrieval faster, simpler and more accessible.

## ✨ Key Features

- **Intelligent Information Retrieval:** Retrieves relevant information from GTBIT's official website and institutional documents.
- **Retrieval-Augmented Generation:** Grounds AI-generated responses in retrieved institutional content.
- **Document Processing:** Extracts and processes information from PDF documents and webpages.
- **Semantic Search:** Uses vector embeddings to identify contextually relevant information.
- **Source Attribution:** Provides references to the sources used to generate responses.
- **Natural Language Interaction:** Allows users to interact with institutional information conversationally.
- **Student-Facing Prototype:** Includes a browser chat interface that can use mock replies or the Flask API.
- **Modular Architecture:** Separates data collection, preprocessing, retrieval and response generation.

## 🧠 How It Works

Info-Bot follows a Retrieval-Augmented Generation architecture consisting of two main stages.

### 1. Knowledge Base Creation

Institutional information is collected and transformed into searchable data.

```text
GTBIT Official Website + PDF Documents
                 |
                 ▼
          Data Collection
                 |
                 ▼
       Text Extraction & Cleaning
                 |
                 ▼
           Text Chunking
                 |
                 ▼
        Embedding Generation
                 |
                 ▼
          ChromaDB Storage
```

### 2. Question Answering

When a user submits a question, the system retrieves relevant information and uses it to generate an answer.

```text
        User Question
              |
              ▼
       Query Embedding
              |
              ▼
      Semantic Retrieval
              |
              ▼
    Relevant Context Retrieval
              |
              ▼
       Gemini Integration
              |
              ▼
      Contextual Answer
              |
              ▼
    Answer + Source References
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Backend API development |
| Google Gemini | Large Language Model for response generation |
| Sentence Transformers | Text embedding generation |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Vector database and similarity search |
| BeautifulSoup | Website scraping |
| Requests | HTTP requests and document downloading |
| pdfplumber | PDF text extraction |
| PyMuPDF | Page rendering for optional scanned-PDF OCR |
| Google GenAI SDK | Gemini answer generation and optional scanned-page OCR |

## 📂 Project Structure

```text
Info-Bot/
│
├── rag/
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── chunking.py
│   ├── embedding.py
│   ├── vector_store.py
│   ├── rag_system.py
│   └── build_chunks.py
│
├── scraper/
│   ├── __init__.py
│   ├── website_scraper.py
│   ├── pdf_downloader.py
│   ├── batch_pdf_downloader.py
│   ├── pdf_extractor.py
│   ├── batch_pdf_processor.py
│   ├── scanned_pdf_ocr.py
│   ├── prepare_dataset.py
│   ├── inspect_page.py
│   └── ocr_scanned_pdf.py
│
├── app.py
├── frontend/
├── .env.example
├── requirements.txt
├── .gitignore
│
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

- Python installed
- Git installed
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/Asiskaurr/Info-Bot-.git
cd Info-Bot-
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment:

**Windows:**
```powershell
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` in the project root, then set your Gemini API key. The configured default is `gemini-3.5-flash-lite`; `GEMINI_MODEL` can be changed to another model available to your API key. The file also contains the local ChromaDB path, local CORS origins and optional OCR setting.

```env
GEMINI_API_KEY=your_gemini_api_key
```

**Important:** Never upload your API key or `.env` file to GitHub.

### 5. Prepare the Knowledge Base

Generated datasets and ChromaDB files are excluded from Git. Run these commands from the repository root, in order:

```bash
python -m scraper.website_scraper
python -m scraper.batch_pdf_downloader
python -m scraper.batch_pdf_processor
python -m scraper.prepare_dataset
python -m rag.build_chunks
python -m rag.vector_store
```

The crawler is limited to 300 pages by default. Set `GTBIT_MAX_PAGES=0` in `.env` to remove that cap. It follows same-site links and extracts static HTML; this still cannot guarantee capture of content that requires browser JavaScript or lives outside the GTBIT host.

Retrieval returns up to five cosine-nearest chunks and drops results above `MAX_RETRIEVAL_DISTANCE` (default `0.65`). Treat this as an initial smoke-build setting: review it against representative answerable and unanswerable questions before relying on it for a larger knowledge base.

Scanned PDF pages are detected during extraction. OCR is opt-in because it sends page images to Gemini and may consume API quota: set `ENABLE_SCANNED_PDF_OCR=true` in `.env` before running `python -m scraper.batch_pdf_processor`. Then continue with dataset preparation, chunking and indexing.

### 6. Start the Backend

Once the knowledge base has been prepared and `.env` contains a valid key, start the API:

```bash
python app.py
```

The Flask development server starts at:

```text
http://127.0.0.1:5000
```

`GET /health` checks that Flask is running. `GET /ready` checks the Gemini key and that the ChromaDB collection exists and contains records. The app can start before data preparation, but chat requests return a clear `503 BACKEND_NOT_READY` response until these requirements are met.

### 7. Run the frontend locally

In a second terminal, from the repository root, serve the page over HTTP:

```bash
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`. In `frontend/app.js`, set `USE_MOCK_API` to `false` to send questions to `http://127.0.0.1:5000/api/chat`. The default CORS allowlist includes this local origin; configure `FRONTEND_ORIGINS` for other origins. Directly opening `index.html` is suitable for mock mode; use the local server for API mode.

## 🔌 API Documentation

The Flask backend exposes the following endpoints.

### Health Check

**Endpoint:** `GET /health`

Checks whether Flask is running. It does not require the vector index or API key.

**Example Response:**

```json
{
  "status": "success",
  "message": "GTBIT chatbot backend is running."
}
```

### Readiness Check

**Endpoint:** `GET /ready`

Returns HTTP 200 when the Gemini key and a non-empty ChromaDB collection are available, or HTTP 503 with an error object when the backend is not ready.

### Chat Endpoint

**Endpoint:** `POST /api/chat`

Accepts a user's question and returns a generated response along with source references.

**Request Body:**

```json
{
  "question": "What departments are available at GTBIT?"
}
```

**Example Response:**

```json
{
  "answer": "GTBIT offers several undergraduate engineering programmes...",
  "sources": [
    {
      "title": "GTBIT Admission Brochure",
      "url": "https://www.gtbit.ac.in/",
      "snippet": "A short excerpt from the retrieved document.",
      "page_number": 2,
      "source_number": 1
    }
  ]
}
```

`snippet` and `page_number` are included when available. No-match questions return a normal answer with `sources: []`. Request and service errors use `{ "error": { "code": "...", "message": "..." } }` and an appropriate HTTP status.

## 🔍 Core Modules

| Module | Description |
|---|---|
| Website Scraper | Collects information from GTBIT's official website |
| PDF Processor | Downloads and extracts text from institutional PDFs |
| Data Cleaning | Cleans and prepares extracted information |
| Chunking | Divides documents into smaller text segments |
| Embedding Generator | Converts text into numerical vector representations |
| Vector Store | Stores embeddings and supports similarity-based retrieval |
| RAG System | Retrieves relevant context and generates answers |
| Flask API | Exposes chatbot functionality through REST endpoints |

## 🚀 Future Enhancements

- Administrative dashboard for knowledge base management.
- Dynamic document uploads and knowledge base updates.
- Improved retrieval accuracy and response evaluation.
- Expanded multilingual interaction.
- Deployment for wider institutional access.

## 👩‍💻 Development

Developed as a collaborative academic project for **Guru Tegh Bahadur Institute of Technology**.

The project brings together backend engineering, information retrieval, natural language processing and frontend development to simplify access to institutional information.

---

<p align="center">
  <b>Making institutional information easier to find, understand and access. 💙</b>
</p>
