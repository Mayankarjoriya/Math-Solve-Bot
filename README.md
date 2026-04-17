# MathSolve AI 🤖

**MathSolve AI** is an intelligent math problem solver that combines **Computer Vision**, **Large Language Models (LLMs)**, and **Retrieval-Augmented Generation (RAG)** to solve math problems from images and PDFs.

## ✨ Features

- 📸 **Image-to-Math**: Upload photos of math problems and get step-by-step solutions
- 📄 **PDF Solver**: Process entire PDF documents to extract and solve math problems
- 🧠 **Smart OCR**: Uses Google Vision AI for high-accuracy text extraction
- 📚 **RAG-Powered**: Retrieves relevant textbook content to improve answer accuracy
- 💬 **Context-Aware**: Maintains conversation history for follow-up questions
- 📊 **Analytics Dashboard**: Track usage, accuracy, and popular topics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Vision API enabled (with billing)
- Ollama server running locally

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mayank030905/Math-Solve-Bot.git
   cd Math-Solve-Bot
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file with your Google Cloud credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Start the backend**
   ```bash
   uvicorn backend.main:app --reload
   ```

6. **Start the frontend**
   ```bash
   streamlit run frontend/app.py
   ```

7. **Open in browser**
   Go to `http://localhost:8501`

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MathSolve AI System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐   ┌───────────────────────────────┐  │
│  │   Frontend      │   │           Backend             │  │
│  │  (Streamlit)    │   │        (FastAPI)              │  │
│  └─────────────────┘   └───────────────────────────────┘  │
│         │                     │                             │
│         ▼                     ▼                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           OCR Service (Google Vision)               │  │
│  └─────────────────────────────────────────────────────┘  │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           RAG Pipeline                                │  │
│  │  - Vector Store (ChromaDB)                          │  │
│  │  - Embedding Model (Sentence Transformers)          │  │
│  │  - PDF Loader                                       │  │
│  └─────────────────────────────────────────────────────┘  │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           LLM Service (Ollama)                      │  │
│  │  - Math-specific models                             │  │
│  │  - Step-by-step reasoning                           │  │
│  └─────────────────────────────────────────────────────┘  │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Database (SQLite)                         │  │
│  │  - User authentication                              │  │
│  │  - Conversation history                             │  │
│  │  - Analytics                                        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
Math-Solve-Bot/
├── backend/                  # FastAPI backend
│   ├── main.py               # API entry point
│   ├── config.py             # Configuration
│   ├── database.py           # Database setup
│   ├── models/               # SQLAlchemy models
│   ├── services/             # Business logic
│   │   ├── ocr_service.py    # OCR implementation
│   │   ├── rag_service.py    # RAG pipeline
│   │   ├── llm_service.py    # LLM integration
│   │   └── auth_service.py   # Authentication
│   └── utils/                # Utility functions
├── frontend/                 # Streamlit frontend
│   ├── app.py                # Main application
│   ├── components/           # Reusable UI components
│   └── assets/               # Images and static files
├── data/                     # Data directory
│   ├── chroma_db/            # Vector database
│   └── uploads/              # Uploaded files
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS="./Vison.json"

# Database
DATABASE_URL="sqlite:///./mathsolve.db"

# Ollama
OLLAMA_HOST="http://localhost:11434"
OLLAMA_MODEL="llama3.1:latest"

# RAG
CHROMA_COLLECTION_NAME="math_problems"
```

## 📚 RAG Setup

### 1. Add Textbook PDFs
Place your math textbook PDFs in the `data/` directory:
```bash
cp textbooks/*.pdf data/
```

### 2. Index the PDFs
Run the indexing script to process and embed the documents:
```bash
python backend/services/rag_service.py --index
```

This will:
- Extract text from PDFs
- Split into chunks
- Generate embeddings
- Store in ChromaDB

## 🤖 Available Models

### OCR
- **Primary**: Google Cloud Vision API (high accuracy)
- **Fallback**: Tesseract OCR (local)

### LLM (Ollama)
- **Default**: `llama3.1:latest`
- **Alternatives**: `qwen2.5:latest`, `mistral:latest`, `gemma3:latest`

### Embeddings
- `sentence-transformers/all-MiniLM-L6-v2`

## 📊 Analytics

Access the analytics dashboard at:
```
http://localhost:8501/admin
```

Features:
- Total questions solved
- Accuracy by topic
- Most common problem types
- User activity

## 🧪 Testing

Run backend tests:
```bash
pytest backend/tests/
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License

## 📞 Support

For issues or questions, please open an issue on GitHub.