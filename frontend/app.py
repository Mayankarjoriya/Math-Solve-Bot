"""
MathSolve AI — Streamlit Frontend
A premium, dark-themed Calculus doubt solver for JEE/Board students.
"""

import streamlit as st
import requests
import uuid
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MathSolve AI — Calculus Solver",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []
if "current_solution" not in st.session_state:
    st.session_state.current_solution = None

# ---------------------------------------------------------------------------
# Custom CSS — Premium Dark Theme with Glassmorphism
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* ---- Import Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ---- Global Styles ---- */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* ---- Hide default Streamlit elements ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ---- Hero Header ---- */
    .hero-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 50%);
        animation: pulse-glow 6s ease-in-out infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.6);
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* ---- Glass Card ---- */
    .glass-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(129,140,248,0.3);
        box-shadow: 0 8px 32px rgba(99,102,241,0.1);
    }
    .glass-card h3 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e0e7ff;
        margin-bottom: 1rem;
    }

    /* ---- Solution Container ---- */
    .solution-container {
        background: linear-gradient(145deg, rgba(15,12,41,0.9), rgba(36,36,62,0.9));
        border: 1px solid rgba(129,140,248,0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
        color: #e2e8f0;
    }
    .solution-container h3 {
        color: #818cf8;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .solution-container strong {
        color: #c4b5fd;
    }

    /* ---- Stat Cards ---- */
    .stat-card {
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(192,132,252,0.1));
        border: 1px solid rgba(129,140,248,0.2);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }

    /* ---- Topic Badge ---- */
    .topic-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.2rem;
        letter-spacing: 0.5px;
    }
    .badge-limits { background: rgba(99,102,241,0.2); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }
    .badge-differentiation { background: rgba(244,114,182,0.2); color: #f472b6; border: 1px solid rgba(244,114,182,0.3); }
    .badge-integration { background: rgba(52,211,153,0.2); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
    .badge-application { background: rgba(251,191,36,0.2); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
    .badge-default { background: rgba(148,163,184,0.2); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }

    /* ---- Difficulty Badge ---- */
    .diff-easy { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); padding: 0.2rem 0.6rem; border-radius: 8px; font-size: 0.7rem; font-weight: 600; }
    .diff-medium { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); padding: 0.2rem 0.6rem; border-radius: 8px; font-size: 0.7rem; font-weight: 600; }
    .diff-hard { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); padding: 0.2rem 0.6rem; border-radius: 8px; font-size: 0.7rem; font-weight: 600; }

    /* ---- History Item ---- */
    .history-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .history-item:hover {
        background: rgba(99,102,241,0.08);
        border-color: rgba(129,140,248,0.2);
    }
    .history-question {
        font-size: 0.9rem;
        color: #cbd5e1;
        margin-bottom: 0.4rem;
        font-weight: 500;
    }
    .history-meta {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
    }

    /* ---- Upload Area ---- */
    .upload-area {
        border: 2px dashed rgba(129,140,248,0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: rgba(99,102,241,0.05);
        transition: all 0.3s ease;
    }
    .upload-area:hover {
        border-color: rgba(129,140,248,0.5);
        background: rgba(99,102,241,0.1);
    }

    /* ---- Sidebar styling ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* ---- Button Override ---- */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa);
        box-shadow: 0 4px 20px rgba(99,102,241,0.4);
        transform: translateY(-1px);
    }

    /* ---- Spinner ---- */
    .solving-animation {
        text-align: center;
        padding: 2rem;
        color: #818cf8;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* ---- Tab styling ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _get_topic_badge_class(topic: str) -> str:
    topic_lower = topic.lower() if topic else ""
    if "limit" in topic_lower or "continuity" in topic_lower:
        return "badge-limits"
    elif "differenti" in topic_lower:
        return "badge-differentiation"
    elif "integr" in topic_lower:
        return "badge-integration"
    elif "application" in topic_lower or "area" in topic_lower:
        return "badge-application"
    return "badge-default"


def _get_diff_class(diff: str) -> str:
    d = diff.lower() if diff else ""
    if d == "easy":
        return "diff-easy"
    elif d == "hard":
        return "diff-hard"
    return "diff-medium"


def _api_healthcheck() -> bool:
    try:
        r = requests.get(f"{API_BASE}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _solve_question(text: str) -> dict:
    try:
        r = requests.post(
            f"{API_BASE}/solve/",
            json={"session_id": st.session_state.session_id, "text": text},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"solution": f"⚠️ Error communicating with backend: {e}", "topic": "Error", "difficulty": "Unknown"}


def _upload_image(file) -> str:
    try:
        r = requests.post(
            f"{API_BASE}/upload-image/",
            files={"file": (file.name, file.getvalue(), file.type)},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("extracted_text", "")
    except Exception as e:
        return f"⚠️ OCR Error: {e}"


def _fetch_history():
    try:
        r = requests.get(f"{API_BASE}/history/{st.session_state.session_id}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def _fetch_stats():
    try:
        r = requests.get(f"{API_BASE}/stats/{st.session_state.session_id}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"total_questions": 0, "topics": {}, "difficulty": {}}


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">🧮</div>
        <div style="font-size: 1.3rem; font-weight: 800; 
              background: linear-gradient(90deg, #818cf8, #c084fc);
              -webkit-background-clip: text; -webkit-text-fill-color: transparent;
              margin-top: 0.3rem;">MathSolve AI</div>
        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">
            Calculus Doubt Solver
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Status
    api_ok = _api_healthcheck()
    if api_ok:
        st.markdown("🟢 **Backend Connected**")
    else:
        st.markdown("🔴 **Backend Offline**")
        st.caption("Start: `uvicorn backend.main:app --reload`")

    st.markdown("---")

    # Session info
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.history = []
        st.session_state.current_solution = None
        st.rerun()

    st.markdown("---")

    # Quick Stats
    stats = _fetch_stats()
    st.markdown("### 📊 Your Progress")
    st.markdown(f"""
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-top:0.5rem;">
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_questions', 0)}</div>
            <div class="stat-label">Solved</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(stats.get('topics', {}))}</div>
            <div class="stat-label">Topics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Topic breakdown
    if stats.get("topics"):
        st.markdown("#### Topics Covered")
        for topic, count in stats["topics"].items():
            badge_class = _get_topic_badge_class(topic)
            st.markdown(
                f'<span class="topic-badge {badge_class}">{topic}</span>'
                f' <span style="color:rgba(255,255,255,0.4); font-size:0.8rem;">× {count}</span>',
                unsafe_allow_html=True,
            )

    # Difficulty breakdown
    if stats.get("difficulty"):
        st.markdown("#### Difficulty Split")
        for diff, count in stats["difficulty"].items():
            diff_class = _get_diff_class(diff)
            st.markdown(
                f'<span class="{diff_class}">{diff}</span>'
                f' <span style="color:rgba(255,255,255,0.4); font-size:0.8rem;">× {count}</span>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Main Content Area
# ---------------------------------------------------------------------------

# Hero Header
st.markdown("""
<div class="hero-header">
    <div class="hero-title">MathSolve AI</div>
    <div class="hero-subtitle">
        Your personal Calculus tutor — powered by AI, built for JEE & Board exams 🚀
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_solve, tab_history, tab_dashboard = st.tabs(["🧠 Solve", "📜 History", "📈 Dashboard"])

# ===========================
# TAB 1: SOLVE
# ===========================
with tab_solve:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="glass-card"><h3>📝 Ask Your Doubt</h3></div>', unsafe_allow_html=True)

        input_method = st.radio(
            "Choose input method:",
            ["✍️ Type Question", "📷 Upload Photo"],
            horizontal=True,
            label_visibility="collapsed",
        )

        extracted_text = ""

        if input_method == "📷 Upload Photo":
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload a photo of your math problem",
                type=["png", "jpg", "jpeg", "webp"],
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                with st.spinner("🔍 Extracting text from image..."):
                    extracted_text = _upload_image(uploaded_file)
                if extracted_text and not extracted_text.startswith("⚠️"):
                    st.success("✅ Text extracted successfully!")
                    st.code(extracted_text, language="text")
                else:
                    st.error(extracted_text)

        question_text = st.text_area(
            "Your Calculus question:",
            value=extracted_text,
            height=150,
            placeholder="e.g., Find the derivative of x^3 * sin(x)\n\nor\n\nEvaluate the integral of (2x+1)/(x^2+x+1) dx",
        )

        solve_col1, solve_col2 = st.columns([1, 1])
        with solve_col1:
            solve_btn = st.button("🚀 Solve It!", use_container_width=True, type="primary")
        with solve_col2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)

        if clear_btn:
            st.session_state.current_solution = None
            st.rerun()


    with col_output:
        st.markdown('<div class="glass-card"><h3>💡 Step-by-Step Solution</h3></div>', unsafe_allow_html=True)

        if solve_btn and question_text.strip():
            with st.spinner(""):
                st.markdown("""
                <div class="solving-animation">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                    Thinking step by step...
                </div>
                """, unsafe_allow_html=True)

                result = _solve_question(question_text.strip())
                st.session_state.current_solution = result

            st.rerun()

        elif solve_btn and not question_text.strip():
            st.warning("Please enter a question first!")

        # Display current solution
        if st.session_state.current_solution:
            result = st.session_state.current_solution

            # Topic and difficulty badges
            topic = result.get("topic", "Calculus")
            diff = result.get("difficulty", "Medium")
            badge_class = _get_topic_badge_class(topic)
            diff_class = _get_diff_class(diff)

            st.markdown(
                f'<span class="topic-badge {badge_class}">{topic}</span> '
                f'<span class="{diff_class}">{diff}</span>',
                unsafe_allow_html=True,
            )
            st.markdown("")

            # Solution in a styled container
            st.markdown(result.get("solution", "No solution generated."))

        else:
            # Empty state
            st.markdown("""
            <div style="text-align:center; padding: 3rem 1rem; color: rgba(255,255,255,0.3);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📐</div>
                <div style="font-size: 1.1rem; font-weight: 500;">Your solution will appear here</div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                    Type a question or upload a photo to get started
                </div>
            </div>
            """, unsafe_allow_html=True)


# ===========================
# TAB 2: HISTORY
# ===========================
with tab_history:
    st.markdown('<div class="glass-card"><h3>📜 Question History</h3></div>', unsafe_allow_html=True)

    history = _fetch_history()

    if not history:
        st.markdown("""
        <div style="text-align:center; padding: 3rem; color: rgba(255,255,255,0.3);">
            <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📭</div>
            <div>No questions solved yet. Start solving to build your history!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in history:
            topic = item.get("topic", "Calculus")
            diff = item.get("difficulty", "Medium")
            badge_class = _get_topic_badge_class(topic)
            diff_class = _get_diff_class(diff)

            with st.expander(f"📌 {item['question'][:80]}{'...' if len(item['question']) > 80 else ''}", expanded=False):
                st.markdown(
                    f'<span class="topic-badge {badge_class}">{topic}</span> '
                    f'<span class="{diff_class}">{diff}</span> '
                    f'<span style="color:rgba(255,255,255,0.3); font-size:0.75rem;">{item.get("created_at", "")}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.markdown(item.get("solution", ""))


# ===========================
# TAB 3: DASHBOARD
# ===========================
with tab_dashboard:
    st.markdown('<div class="glass-card"><h3>📈 Progress Dashboard</h3></div>', unsafe_allow_html=True)

    stats = _fetch_stats()

    # Top-level stat cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_questions', 0)}</div>
            <div class="stat-label">Total Solved</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(stats.get('topics', {}))}</div>
            <div class="stat-label">Topics Covered</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        hard_count = stats.get("difficulty", {}).get("Hard", 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{hard_count}</div>
            <div class="stat-label">Hard Problems</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Charts
    if stats.get("topics"):
        st.markdown("### 📊 Topic Distribution")
        import pandas as pd
        topic_df = pd.DataFrame(
            list(stats["topics"].items()),
            columns=["Topic", "Count"]
        )
        st.bar_chart(topic_df.set_index("Topic"), color="#818cf8")

    if stats.get("difficulty"):
        st.markdown("### 🎯 Difficulty Distribution")
        diff_df = pd.DataFrame(
            list(stats["difficulty"].items()),
            columns=["Difficulty", "Count"]
        )
        st.bar_chart(diff_df.set_index("Difficulty"), color="#c084fc")

    if not stats.get("topics") and not stats.get("difficulty"):
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:rgba(255,255,255,0.3);">
            <div style="font-size:2.5rem; margin-bottom:0.8rem;">📊</div>
            <div>Solve some problems to see your progress analytics here!</div>
        </div>
        """, unsafe_allow_html=True)
