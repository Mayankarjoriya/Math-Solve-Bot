from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from backend.services.ocr_service import extract_text_from_image
from backend.services.llm_service import get_llm_solution
from backend.services.rag_service import query_rag, ingest_pdfs
# Import our database setup and models
from backend.database import engine, get_db
from backend.models import schemas
import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# load .env file
load_dotenv()

# Create database tables
schemas.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MathSolve AI Backend",
    description="AI-powered Calculus doubt solver for JEE/Board students",
    version="1.0.0",
)

# Setup CORS so the Streamlit frontend can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema for incoming text queries
class QuestionRequest(BaseModel):
    session_id: str
    text: str

@app.get("/")
def read_root():
    return {"status": "MathSolve AI API is running"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Receives a photo of a handwritten question and extracts text using OCR.
    Falls back to Tesseract if Google Vision API is unavailable.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    # Read the file into bytes
    image_bytes = await file.read()
    
    # Run the OCR service (Google Vision → Tesseract fallback)
    extracted_text = extract_text_from_image(image_bytes)
    
    return {
        "filename": file.filename, 
        "extracted_text": extracted_text
    }


@app.post("/solve/")
def solve_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """
    Takes a text question, retrieves relevant textbook context via RAG,
    runs it through the local Gemma LLM, and saves to DB.
    """
    logger.info(f"Received question from session {request.session_id}: {request.text[:80]}...")

    # Step 1: Query RAG for relevant calculus textbook context
    rag_context = query_rag(request.text)
    
    # Step 2: Send question + context to the local LLM
    llm_result = get_llm_solution(
        question_text=request.text,
        rag_context=rag_context,
    )
    
    solution_text = llm_result["solution"]
    topic_tag = llm_result["topic"]
    difficulty_level = llm_result["difficulty"]
    
    # Step 3: Save the interaction to the database for the progress dashboard
    new_history = schemas.QuestionHistory(
        session_id=request.session_id,
        original_text=request.text,
        solution_text=solution_text,
        topic_tag=topic_tag,
        difficulty_level=difficulty_level,
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    
    return {
        "question_id": new_history.id,
        "solution": new_history.solution_text,
        "topic": new_history.topic_tag,
        "difficulty": new_history.difficulty_level,
    }


@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """
    Returns the question history for a given session, ordered by most recent.
    Used by the frontend progress dashboard.
    """
    records = (
        db.query(schemas.QuestionHistory)
        .filter(schemas.QuestionHistory.session_id == session_id)
        .order_by(schemas.QuestionHistory.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "question": r.original_text,
            "solution": r.solution_text,
            "topic": r.topic_tag,
            "difficulty": r.difficulty_level,
            "created_at": str(r.created_at),
        }
        for r in records
    ]


@app.get("/stats/{session_id}")
def get_stats(session_id: str, db: Session = Depends(get_db)):
    """
    Returns aggregated stats for the progress dashboard.
    """
    total = (
        db.query(func.count(schemas.QuestionHistory.id))
        .filter(schemas.QuestionHistory.session_id == session_id)
        .scalar()
    )

    # Topic distribution
    topic_counts = (
        db.query(schemas.QuestionHistory.topic_tag, func.count(schemas.QuestionHistory.id))
        .filter(schemas.QuestionHistory.session_id == session_id)
        .group_by(schemas.QuestionHistory.topic_tag)
        .all()
    )

    # Difficulty distribution
    diff_counts = (
        db.query(schemas.QuestionHistory.difficulty_level, func.count(schemas.QuestionHistory.id))
        .filter(schemas.QuestionHistory.session_id == session_id)
        .group_by(schemas.QuestionHistory.difficulty_level)
        .all()
    )

    return {
        "total_questions": total,
        "topics": {t: c for t, c in topic_counts},
        "difficulty": {d: c for d, c in diff_counts},
    }


@app.post("/ingest-pdfs/")
def trigger_ingest():
    """
    Manually triggers PDF ingestion for the RAG pipeline.
    Place your Calculus PDFs in data/raw_pdfs/ before calling this.
    """
    success = ingest_pdfs()
    if success:
        return {"status": "PDF ingestion successful"}
    raise HTTPException(status_code=500, detail="PDF ingestion failed. Check logs.")