# The Monk AI - Advanced RAG Pipeline for Hindu Scriptures

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Endee](https://img.shields.io/badge/Endee-Vector%20Database-orange)](https://github.com/endee-io/endee)

> **Internship Project for Endee Labs** | A sophisticated AI-powered spiritual knowledge assistant

## Project Overview

**Problem Statement:**
Hindu scriptures contain profound spiritual wisdom, but accessing this knowledge is challenging due to:
- Language barriers (Sanskrit texts with complex translations)
- Information scattered across multiple texts (Bhagavad Gita, Upanishads, Puranas, etc.)
- Difficulty in finding relevant teachings for specific life situations
- Lack of modern search and conversational interfaces

**Solution:**
The Monk AI is an advanced Retrieval-Augmented Generation (RAG) pipeline that enables intelligent, conversational access to Hindu scriptures. Using **Endee as the vector database**, the system provides semantic search, personalized responses, and multilingual support (English + Hindi).

## System Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  FastAPI Backend │────▶│  Endee Vector   │
│   (Main Server)  │     │     Database    │
└────────┬────────┘     └────────┬────────┘
         │                        │
         │                 ┌──────┴──────┐
         │                 │             │
         │                 ▼             ▼
         │       ┌─────────────────┐ ┌──────────────┐
         │       │ Semantic Search │ │  Re-ranking  │
         │       └────────┬────────┘ └──────┬───────┘
         │                │                 │
         │                └────────┬────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   Groq LLM    │◀─────│  Top-K Context  │
│  (llama-3.3)  │       │   Retrieved     │
└────────┬────────┘       └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Enhanced Response               │
│  • Spiritual Teaching                    │
│  • Hindi Translation                     │
│  • Keyword Explanations                  │
│  • Book Recommendations                  │
│  • Source Citations                      │
└─────────────────────────────────────────┘
```

## How Endee is Used

**Endee** serves as the core vector database for this project, enabling:

### 1. Vector Storage & Indexing
- **Index:** `monk_ai_knowledge`
- **Dimension:** 384 (using all-MiniLM-L6-v2 embeddings)
- **Distance Metric:** Cosine Similarity
- **Precision:** FLOAT32
- **Documents:** ~35MB of Hindu scriptures (10 JSONL files)

### 2. Semantic Search Pipeline
```python
# 1. Convert user query to embedding
query_embedding = model.encode(user_query)

# 2. Search in Endee for similar documents
results = endee_client.vector_search(
    index_name="monk_ai_knowledge",
    vector=query_embedding,
    top_k=15
)

# 3. Re-rank with CrossEncoder for accuracy
reranked = cross_encoder.rerank(results, top_k=5)

# 4. Send to LLM for response generation
```

### 3. Key Features Utilized
- **Batch Upserts:** Efficient bulk document loading
- **Metadata Filtering:** Search by book_name, chapter, verse
- **Index Statistics:** Monitor document count and health
- **REST API Integration:** Direct HTTP calls to Endee server

### 4. Migration Benefits
See `MIGRATION_SUMMARY.md` for details on the transition from ChromaDB to Endee, highlighting:
- Client-server architecture
- Better scalability
- Multiple distance metrics
- Quantization support

## Features

✅ **Semantic Search** - Find relevant verses using natural language
✅ **RAG Pipeline** - Grounded responses with source citations
✅ **Multi-modal Input** - Text and voice queries (Whisper)
✅ **Hindi Translation** - Automatic Hindi response translation
✅ **Re-ranking** - CrossEncoder for improved relevance
✅ **User Authentication** - Secure JWT-based auth
✅ **Chat History** - Persistent MongoDB-backed conversations
✅ **Beginner/Expert Modes** - Tailored explanations

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- Endee Vector Database (Docker)
- Groq API Key (get from [console.groq.com](https://console.groq.com))

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/Vaibhav13Shukla/endee.git
cd endee

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Start Endee Vector Database

```bash
cd endee
docker-compose up -d
```

### 4. Load Knowledge Base

```bash
python knowledge_base_loader.py
```

### 5. Start the Application

```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
streamlit run frontend/streamlit_app.py
```

### 6. Access the Application

- **API Documentation:** http://localhost:8000/docs
- **Streamlit UI:** http://localhost:8501

## Project Structure

```
the_monk_ai/
├── main.py                     # FastAPI application entry
├── config/
│   └── config.py              # Configuration settings
├── services/
│   ├── vector_store.py        # Endee integration
│   ├── rag_pipeline.py        # RAG orchestration
│   ├── llm_service.py         # LLM & Groq integration
│   ├── chat_service.py        # Chat session management
│   ├── auth.py                # Authentication
│   └── document_processor.py  # Data processing
├── models/
│   └── database.py            # Pydantic models
├── database/
│   └── connection.py          # MongoDB connection
├── frontend/
│   └── streamlit_app.py       # Web interface
├── data/                      # Scripture files (JSONL)
├── tests/                     # Test suite
├── endee/
│   └── docker-compose.yml     # Endee server setup
└── requirements.txt           # Dependencies
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI + Uvicorn |
| **Vector Database** | **Endee** (https://github.com/endee-io/endee) |
| **LLM** | Groq API (llama-3.3-70b-versatile) |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) |
| **Re-ranking** | CrossEncoder (ms-marco-MiniLM-L-6-v2) |
| **Document Store** | MongoDB |
| **Frontend** | Streamlit |
| **Audio** | Whisper (via Groq) |
| **Translation** | Google Translate |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Authenticate user |
| `/chat/query` | POST | Process text query |
| `/chat/voice-query` | POST | Process voice query |
| `/chat/sessions` | GET | List chat sessions |
| `/system/health` | GET | Health check |
| `/system/stats` | GET | System statistics |

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=services tests/
```

## Documentation

- `README.md` - Project overview (this file)
- `ENDEE_API_GUIDE.md` - Complete Endee API usage guide
- `MIGRATION_SUMMARY.md` - ChromaDB → Endee migration details
- `SYSTEM_STATUS_REPORT.md` - System health documentation

## Mandatory Repository Usage Steps

As per internship requirements:

1. ⭐ **Star the official Endee repository:** https://github.com/endee-io/endee
2. 🍴 **Fork the repository** to your personal GitHub account
3. 🏗️ **Use the forked version** as the base for building this project

## License

This project is built as part of the Endee Labs Internship Program.

---

## Detailed Code Documentation

Below is a detailed explanation of each code file, its purpose, and functionality.

***

### 📂 **Project Structure & Core Logic**

The project is logically divided into folders for configuration (`config`), data handling (`data`, `database`), application layers (`frontend`, `services`, `models`), and utility scripts (`scripts`).

---

### 📄 `main.py`
*   **Use Case:** This is the main entry point for the backend application. It sets up the FastAPI server, defines all the API endpoints, and manages the application's lifecycle (startup and shutdown).
*   **Code Explanation:**
    *   **`lifespan(app: FastAPI)`:** This special function manages startup and shutdown events.
        *   On **startup**, it connects to the MongoDB database and initializes the RAG pipeline. The comment `--- THIS BLOCK HAS BEEN REMOVED ---` correctly notes that the knowledge base should be built separately by a script, not every time the server starts, which is a crucial design choice for efficiency.
        *   On **shutdown**, it closes the connection to MongoDB.
    *   **`app = FastAPI(...)`**: Creates an instance of the FastAPI application, setting metadata like the title and description.
    *   **`app.add_middleware(CORSMiddleware, ...)`**: Configures Cross-Origin Resource Sharing (CORS) to allow the frontend (running on a different domain) to communicate with this backend API.
    *   **API Endpoints (`@app.post(...)`, `@app.get(...)`)**: Each function defines a specific API endpoint.
        *   **/auth/**: Endpoints for user registration (`/register`), login (`/login`), and fetching user data (`/me`). They use functions from `services.auth`.
        *   **/chat/query**: The primary endpoint for processing text-based queries. It takes a user's question, passes it to the `RAGPipeline`, and returns a structured response. It requires user authentication.
        *   **/chat/voice-query**: Handles audio file uploads for voice-based queries. It saves the audio temporarily, sends it to the `RAGPipeline` for transcription and processing, and returns a response.
        *   **/chat/sessions/**: Endpoints for managing chat history, including fetching all sessions, getting a specific session's messages, deleting a session, and updating a session's title. These endpoints interact with the `ChatService`.
        *   **/system/**: Endpoints for monitoring the application's health (`/health`) and getting statistics about the RAG pipeline (`/stats`).
    *   **`if __name__ == "__main__":`**: This block allows the server to be run directly for development using `uvicorn`.

---

### 📂 `services`

This directory contains the core logic of the application, separated into different services for modularity.

#### 📄 `rag_pipeline.py`
*   **Use Case:** This file orchestrates the entire RAG process. It acts as the central coordinator that uses the vector store and the LLM service to generate a final answer.
*   **Code Explanation:**
    *   **`RAGPipeline` Class:**
        *   **`__init__(self)`**: Initializes instances of `VectorStore`, `LLMService`, and `ChatService`.
        *   **`initialize(self)`**: A method to ensure the vector store connection is established.
        *   **`process_query(...)`**: The main workflow for a text query.
            1.  It calls `preprocess_query` to clean the input.
            2.  It uses `self.vector_store.search_and_rerank()` to retrieve the most relevant documents.
            3.  If no documents are found, it returns a fallback message.
            4.  It calls `self.llm_service.generate_response()` with the query and the retrieved documents to get the final answer.
            5.  It translates the response to Hindi.
            6.  It calls `handle_chat_session()` to save the user's query and the AI's response to the database.
            7.  It packages everything into a `QueryResponse` model and returns it.
        *   **`process_voice_query(...)`**: The main workflow for a voice query.
            1.  It calls `self.llm_service.transcribe_audio()` to convert the audio file to text.
            2.  It then calls `self.process_query()` with the transcribed text.
            3.  It ensures the temporary audio file is deleted.
        *   **`handle_chat_session(...)`**: Manages the conversation history. If it's a new chat, it creates a new session; otherwise, it adds the new messages to the existing session.

#### 📄 `llm_service.py`
*   **Use Case:** This service is responsible for all interactions with the large language models (LLMs) and external APIs, including response generation, audio transcription, and translation.
*   **Code Explanation:**
    *   **`LLMService` Class:**
        *   **`__init__(self)`**: Initializes the `Groq` client with the API key for fast LLM inference.
        *   **`identify_and_explain_keywords(...)`**: An advanced feature for "beginner" mode. It uses a small, fast LLM (`llama3-8b-8192`) to identify key spiritual terms in the generated text and then uses Google Search to find simple definitions for them.
        *   **`get_book_recommendations(...)`**: Extracts the names of the source books from the metadata of the retrieved documents to recommend further reading.
        *   **`create_prompt(...)`**: Dynamically creates the prompt for the LLM. It assembles the retrieved context and the user's query into a detailed instruction set, which changes depending on whether the user is in "beginner" or "expert" mode.
        *   **`generate_response(...)`**: Sends the final prompt to the Groq API to get the AI's answer. It also orchestrates calling the keyword explanation and citation extraction functions.
        *   **`extract_citations(...)`**: Extracts metadata from the retrieved documents to provide sources for the generated answer.
        *   **`translate_to_hindi(...)`**: Uses the `deep_translator` library to translate the final response into Hindi.
        *   **`transcribe_audio(...)`**: Sends an audio file to the Groq API, which uses a Whisper model to transcribe the speech into text.

#### 📄 `vector_store.py`
*   **Use Case:** This service manages all operations related to the Endee vector database. This includes creating and storing embeddings, retrieving documents, and re-ranking them.
*   **Code Explanation:**
    *   **`VectorStore` Class:**
        *   **`__init__(self)`**:
            *   Loads the embedding model (`HuggingFaceEmbeddings`) which turns text into vectors.
            *   Loads the re-ranking model (`CrossEncoder`).
            *   Initializes the `endee.Endee()` client, which connects to the Endee vector database server.
        *   **`initialize_vectorstore(self)`**: Creates or connects to the Endee index where the scripture embeddings are stored. It checks if the index exists, and if not, creates a new one with the configured dimension and distance metric.
        *   **`add_documents(...)`**: Takes a list of document chunks and adds them to the vector store. It processes them in batches for efficiency.
        *   **`similarity_search(...)`**: Performs the initial, fast retrieval step. Given a query, it finds the `k` most similar document chunks from the database based on vector similarity.
        *   **`rerank_documents(...)`**: This is a key advanced RAG step. It takes the documents from the similarity search and uses the more powerful `CrossEncoder` model to re-score them specifically against the query. This significantly improves the relevance of the final documents.
        *   **`search_and_rerank(...)`**: Combines the two steps above into a single pipeline for efficient retrieval.
        *   **`get_collection_stats(self)`**: Returns statistics about the database, such as the total number of documents.

#### 📄 `document_processor.py`
*   **Use Case:** This service is responsible for reading raw data files (CSV, TXT, JSONL), processing them, and splitting them into smaller, manageable chunks suitable for embedding.
*   **Code Explanation:**
    *   **`DocumentProcessor` Class:**
        *   **`__init__(self, ...)`**: Initializes a `RecursiveCharacterTextSplitter` from the LangChain library, which is a smart text splitter that tries to keep related text together.
        *   **`csv_to_jsonl(...)`, `txt_to_jsonl(...)`**: Utility functions to convert different data formats into a standardized JSONL (JSON Lines) format, where each line is a JSON object with "content" and "metadata".
        *   **`load_jsonl_documents(...)`**: Reads the standardized JSONL file and loads the data into LangChain's `Document` objects.
        *   **`chunk_documents(...)`**: Takes the loaded documents and uses the `text_splitter` to break them down into smaller chunks. It carefully preserves the metadata for each chunk.
        *   **`process_all_data(...)`**: The main function that iterates through a directory, processes all supported file types, and returns a final list of all chunked documents ready to be added to the vector store.

#### 📄 `chat_service.py` & `auth.py`
*   **Use Case:**
    *   `chat_service.py`: Handles all business logic related to chat sessions, such as creating, retrieving, and updating conversations in the MongoDB database.
    *   `auth.py`: Manages user authentication and authorization, including password hashing, token creation, and user verification.
*   **Code Explanation:**
    *   **`ChatService` Class**: Contains methods (`create_chat_session`, `add_message_to_session`, etc.) that perform CRUD (Create, Read, Update, Delete) operations on the `chat_sessions` collection in MongoDB. It uses `ObjectId` to correctly reference users and sessions.
    *   **`auth.py` Functions**:
        *   `verify_password`, `get_password_hash`: Use `passlib` for secure password handling.
        *   `create_access_token`: Creates a JWT (JSON Web Token) that authenticates the user for a set period.
        *   `authenticate_user`: Checks if a user's email and password are valid.
        *   `get_current_active_user`: A FastAPI dependency that protects endpoints by ensuring the user provides a valid token.

---

### 📂 `database` & `models`

#### 📄 `database/connection.py`
*   **Use Case:** Manages the connection to the MongoDB database.
*   **Code Explanation:**
    *   **`connect_to_mongo()`**: Establishes the connection to the MongoDB server using the `motor` library (an asynchronous Python driver for MongoDB). It also calls `create_indexes()` to ensure efficient database queries.
    *   **`close_mongo_connection()`**: Closes the database connection gracefully.
    *   **`create_indexes()`**: Creates indexes on fields like `email` (for users) and `user_id` (for chat sessions) to speed up database lookups significantly.

#### 📄 `models/database.py`
*   **Use Case:** Defines the data structures for the application using Pydantic. This ensures that data exchanged between the API and other parts of the system is well-formed and validated.
*   **Code Explanation:**
    *   **`PyObjectId` Class**: A custom type to properly handle MongoDB's `ObjectId` within Pydantic models.
    *   **`UserCreate`, `UserLogin`, `User`**: Models for user registration, login, and the user data stored in the database.
    *   **`ChatMessage`, `ChatSession`**: Models that define the structure of a single message and a full conversation session.
    *   **`QueryRequest`, `QueryResponse`**: These are crucial models that define the structure of the data sent to the `/chat/query` endpoint and the detailed response that the API returns.
    *   **`Token`, `TokenData`**: Models for the JWT authentication token.

---

### 📂 `scripts` & Root Files

#### 📄 `scripts/initialize_data.py` / `knowledge_base_loader.py`
*   **Use Case:** A one-time setup script to populate the vector database. This script is meant to be run manually before starting the application for the first time.
*   **Code Explanation:**
    *   The script follows the same logic as the data processing pipeline: it finds data files, uses `DocumentProcessor` to load and chunk them, and then uses `VectorStore` to add them to Endee.
    *   It also includes a helpful `create_sample_data()` function that generates sample CSV, TXT, and JSONL files if the `data` directory is empty, making it easy for a new user to test the application without providing their own data.

#### 📄 `knowledge_base_loader.py`
*   **Use Case:** This appears to be an earlier or alternative version of `scripts/initialize_data.py`. Both files serve the same purpose: to process source documents and load them into the vector database. The version in the `scripts` folder is more likely the final, intended version due to its location.
*   **Code Explanation:** The code is very similar to `initialize_data.py`, orchestrating the document processing and vector store loading.

#### 📄 `config/config.py`
*   **Use Case:** Centralizes all configuration settings for the application.
*   **Code Explanation:**
    *   It uses `dotenv` to load environment variables from a `.env` file, which is a best practice for keeping secrets (like API keys) out of the code.
    *   The `Config` class holds static variables for database URLs, API keys, JWT secret key, and various model parameters (like `CHUNK_SIZE`, `LLM_MODEL`, `TOP_K_RETRIEVAL`) that can be easily tuned without changing the application logic.

#### 📄 `requirements.txt`
*   **Use Case:** Lists all the Python libraries and their specific versions required to run the project. This ensures that the application runs in a consistent and reproducible environment.

---

### 📂 `frontend`

#### 📄 `frontend/streamlit_app.py`
*   **Use Case:** Provides a user-friendly web interface for interacting with the backend API.
*   **Code Explanation:**
    *   It uses the `streamlit` library to build the UI.
    *   **`st.session_state`**: Streamlit's mechanism for storing variables across user interactions, used here to keep track of login status, user info, and chat history.
    *   **`login_page()`**: Renders the login and registration forms. It makes API calls to the `/auth/login` and `/auth/register` endpoints on the backend.
    *   **`chat_interface()`**: The main chat view, which appears after login. It includes the chat history display area and an input box for the user to type questions.
    *   **`process_query(...)`**: This function is triggered when the user sends a message. It packages the user's input and sends it to the appropriate backend endpoint (`/chat/query` or `/chat/voice-query`).
    *   **`display_chat_history()`**: Renders the conversation. For assistant messages, it also beautifully formats and displays the extra information like Hindi translations, keyword explanations, citations, and book recommendations returned by the advanced RAG pipeline.
    *   **`sidebar()`**: Creates a sidebar that lists recent chat sessions and allows the user to start a new chat. It fetches this data from the `/chat/sessions` endpoint.