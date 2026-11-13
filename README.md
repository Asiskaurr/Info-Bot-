# 🤖 Info-Bot
### An AI-Powered Information Chatbot for Guru Tegh Bahadur Institute of Technology (GTBIT)

<p align="center">
  <b>Making college information easier to access, one question at a time.</b>
</p>

---

## 🌟 About the Project

**Info-Bot** is an AI-powered college information chatbot designed to provide students with quick, reliable and context-aware answers to their queries about Guru Tegh Bahadur Institute of Technology (GTBIT).

The system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from GTBIT's official website and institutional documents before generating responses using a Large Language Model (LLM).

Instead of manually navigating through multiple webpages and PDF documents, students can simply ask questions in natural language.

## ✨ Key Features

- 🔎 **Intelligent Information Retrieval:** Finds relevant information from the college knowledge base.
- 🧠 **RAG-Based Responses:** Generates answers grounded in retrieved institutional information.
- 📄 **Website and PDF Integration:** Processes information from the official GTBIT website and college documents.
- 💬 **Natural Language Interaction:** Allows students to ask questions conversationally.
- 🔗 **Source Attribution:** Provides references to the information used to generate responses.
- 🌐 **Multilingual Support:** Designed to respond in the language used by the user.
- ⚙️ **Admin Knowledge Base Management:** Supports future integration of an admin dashboard for updating institutional information.

## 🏗️ System Architecture

The project follows a Retrieval-Augmented Generation architecture.

```text
       GTBIT Website + PDF Documents
                    |
                    ▼
          Data Collection Layer
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
             ChromaDB
             (Vector Store)
                    |
                    ▼
          User Submits Question
                    |
                    ▼
          Query Embedding
                    |
                    ▼
         Relevant Context Retrieval
                    |
                    ▼
          Gemini LLM Integration
                    |
                    ▼
           Generated Response
                    |
                    ▼
        Answer + Source References
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Scraping | Requests, BeautifulSoup |
| PDF Processing | PyMuPDF, PyPDF |
| Data Processing | Python |
| Embedding Model | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Database | ChromaDB |
| Large Language Model | Google Gemini |
| Backend Framework | Flask |
| API Communication | REST API |

## 📊 Current Backend Progress

| Module | Implementation |
|---|---|
| Website Scraping | ✅ Completed |
| PDF Downloading | ✅ Completed |
| PDF Text Extraction | ✅ Completed |
| Data Cleaning | ✅ Completed |
| Dataset Preparation | ✅ Completed |
| Text Chunking | ✅ Completed |
| Embedding Generation | ✅ Completed |
| Vector Database Setup | ✅ Completed |
| RAG Pipeline | ✅ Implemented and tested |
| Gemini Integration | ✅ Implemented and tested |
| Flask API | ✅ Implement
