from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.database import Base

class QuestionHistory(Base):
    __tablename__ = "question_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) # To track individual user sessions
    original_text = Column(Text, nullable=False) # The OCR extracted text or typed query
    solution_text = Column(Text, nullable=False) # The generated RAG solution
    difficulty_level = Column(String, default="Medium") # e.g., Easy, Medium, Hard
    topic_tag = Column(String) # e.g., Limits, Derivatives, Integration
    created_at = Column(DateTime, default=datetime.utcnow)