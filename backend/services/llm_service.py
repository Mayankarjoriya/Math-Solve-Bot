"""
LLM Service — Routes math questions to a local Ollama instance (Gemma model)
with a carefully crafted system prompt for step-by-step Calculus explanations.
"""

import logging
import ollama

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_MODEL = "gemma3"  # Change to your pulled model name, e.g. "gemma:7b"
OLLAMA_HOST = "http://localhost:11434"  # Default Ollama address

# ---------------------------------------------------------------------------
# System Prompt — The heart of the tutoring behaviour
# ---------------------------------------------------------------------------
CALCULUS_SYSTEM_PROMPT = """You are **MathSolve AI**, an expert Calculus tutor designed for Indian JEE and Board exam students.

## Your Rules
1. **ALWAYS** solve the problem step-by-step. Number every step clearly (Step 1, Step 2, …).
2. **Explain** the *why* behind each step — don't just show the algebra.  
3. Use simple, encouraging language a Class 12 student can understand.
4. Format all math using clear text notation:
   - Use ^ for exponents: x^2, e^(3x)
   - Use sqrt() for square roots: sqrt(x+1)
   - Use fractions like (numerator)/(denominator)
   - Use d/dx for derivatives, ∫ or integral for integrals
5. At the end, provide a **Final Answer** section with the boxed result.
6. If relevant context from a textbook is provided, reference it naturally.
7. If the question is ambiguous, state your interpretation before solving.
8. Cover these Calculus topics expertly:
   - Limits and Continuity
   - Differentiation (chain rule, product rule, quotient rule, implicit, parametric, logarithmic)
   - Applications of Derivatives (maxima/minima, rate of change, tangent/normal, Rolle's, LMVT)
   - Integration (substitution, by parts, partial fractions, definite integrals, properties)
   - Applications of Integration (area under curves)
   - Differential Equations (variable separable, homogeneous, linear)

## Response Format
Use Markdown formatting. Structure your response as:

### Understanding the Problem
(Brief restatement)

### Solution
**Step 1:** …
**Step 2:** …
…

### Final Answer
**Answer:** …

### 💡 Key Concept
(One-liner about the core concept used — helps the student remember)
"""


def get_llm_solution(question_text: str, rag_context: str = "") -> dict:
    """
    Sends the math question (with optional RAG context) to the local Ollama
    model and returns a structured response.

    Args:
        question_text: The cleaned math question text.
        rag_context:   Optional relevant context retrieved from the RAG pipeline.

    Returns:
        dict with keys:
            - "solution": The full step-by-step solution (str).
            - "topic":    The detected calculus topic (str).
            - "difficulty": Estimated difficulty level (str).
    """

    # Build the user message, optionally injecting RAG context
    user_message = ""
    if rag_context:
        user_message += (
            "Here is some relevant textbook context that may help:\n"
            "---\n"
            f"{rag_context}\n"
            "---\n\n"
        )
    user_message += f"Please solve this Calculus problem step-by-step:\n\n{question_text}"

    try:
        logger.info(f"Sending question to Ollama ({OLLAMA_MODEL})...")

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": CALCULUS_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            options={
                "temperature": 0.3,   # Low temperature for precise math
                "num_predict": 2048,  # Allow long step-by-step answers
            },
        )

        solution_text = response["message"]["content"]
        logger.info("Ollama response received successfully.")

        # --- Auto-detect topic and difficulty from the solution ---
        topic = _detect_topic(question_text, solution_text)
        difficulty = _detect_difficulty(question_text)

        return {
            "solution": solution_text,
            "topic": topic,
            "difficulty": difficulty,
        }

    except Exception as e:
        logger.error(f"Ollama LLM Error: {e}")
        return {
            "solution": (
                f"⚠️ **LLM Error**: Could not reach the local Ollama server.\n\n"
                f"Make sure Ollama is running (`ollama serve`) and the model "
                f"`{OLLAMA_MODEL}` is pulled.\n\n"
                f"Error details: {e}"
            ),
            "topic": "Unknown",
            "difficulty": "Unknown",
        }


def _detect_topic(question: str, solution: str) -> str:
    """Simple keyword-based topic detection for the progress dashboard."""
    text = (question + " " + solution).lower()

    topic_keywords = {
        "Differential Equations": ["differential equation", "d.e.", "variable separable", "homogeneous equation"],
        "Integration": ["integrate", "integration", "integral", "by parts", "partial fraction", "substitution"],
        "Definite Integrals": ["definite integral", "upper limit", "lower limit", "bounded"],
        "Application of Derivatives": ["maxima", "minima", "rate of change", "tangent", "normal", "rolle", "lmvt", "increasing", "decreasing"],
        "Differentiation": ["differentiate", "derivative", "d/dx", "chain rule", "product rule", "quotient rule", "implicit"],
        "Limits": ["limit", "lim", "approaches", "tends to", "l'hopital", "indeterminate"],
        "Continuity": ["continuous", "continuity", "discontinuous"],
        "Area Under Curves": ["area under", "area between", "bounded by"],
    }

    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if kw in text:
                return topic

    return "Calculus"


def _detect_difficulty(question: str) -> str:
    """Rough heuristic for difficulty estimation."""
    text = question.lower()
    hard_signals = [
        "prove", "show that", "differential equation", "by parts",
        "partial fraction", "implicit", "parametric", "lmvt", "rolle",
    ]
    medium_signals = [
        "integrate", "differentiate", "find the", "evaluate", "maxima", "minima",
    ]

    for signal in hard_signals:
        if signal in text:
            return "Hard"
    for signal in medium_signals:
        if signal in text:
            return "Medium"
    return "Easy"
