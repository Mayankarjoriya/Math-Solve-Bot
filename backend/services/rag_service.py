"""
RAG Service — Retrieval-Augmented Generation pipeline for Calculus content.

Ingests Calculus PDF documents from data/raw_pdfs/, chunks them with an
equation-aware strategy, stores embeddings in a local ChromaDB instance,
and provides a query interface to retrieve relevant context.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # Math-Solve-Bot/
PDF_DIR = PROJECT_ROOT / "data" / "raw_pdfs"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

# ---------------------------------------------------------------------------
# Lazy-loaded global index (loaded once on first query)
# ---------------------------------------------------------------------------
_query_engine = None


def _get_or_build_index():
    """
    Returns a LlamaIndex query engine backed by ChromaDB.
    If a persisted index exists in data/chroma_db, it loads from there.
    Otherwise, it ingests PDFs and builds the index from scratch.
    """
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    try:
        import chromadb
        from llama_index.core import (
            VectorStoreIndex,
            SimpleDirectoryReader,
            Settings,
            StorageContext,
        )
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.vector_stores.chroma import ChromaVectorStore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.llms.ollama import Ollama
    except ImportError as e:
        logger.error(f"RAG dependencies not installed: {e}")
        raise

    # --- Configure LlamaIndex to use local models ---
    Settings.llm = Ollama(model="gemma3", request_timeout=120.0)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # --- Setup ChromaDB ---
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    chroma_collection = chroma_client.get_or_create_collection("calculus_docs")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # --- Check if we already have indexed documents ---
    if chroma_collection.count() > 0:
        logger.info(
            f"Loading existing ChromaDB index ({chroma_collection.count()} chunks)..."
        )
        index = VectorStoreIndex.from_vector_store(vector_store)
    else:
        # --- Ingest PDFs ---
        if not PDF_DIR.exists() or not list(PDF_DIR.glob("*.pdf")):
            logger.warning(
                f"No PDFs found in {PDF_DIR}. RAG will return empty context. "
                f"Add your Calculus PDFs to data/raw_pdfs/ and restart."
            )
            _query_engine = _build_empty_engine()
            return _query_engine

        logger.info(f"Ingesting PDFs from {PDF_DIR}...")
        documents = SimpleDirectoryReader(
            input_dir=str(PDF_DIR),
            required_exts=[".pdf"],
        ).load_data()
        logger.info(f"Loaded {len(documents)} document pages.")

        # --- Equation-aware chunking ---
        # We use a larger chunk size to avoid splitting equations mid-line.
        # The paragraph_separator helps keep equation blocks together.
        node_parser = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=128,
            paragraph_separator="\n\n",
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[node_parser],
            show_progress=True,
        )
        logger.info(
            f"Indexing complete. {chroma_collection.count()} chunks stored in ChromaDB."
        )

    _query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="no_text",  # We only want retrieved nodes, not a synthesized answer
    )
    return _query_engine


def _build_empty_engine():
    """Returns a dummy engine that returns empty context when no PDFs are loaded."""

    class _EmptyEngine:
        def query(self, *args, **kwargs):
            class _EmptyResponse:
                source_nodes = []
            return _EmptyResponse()

    return _EmptyEngine()


def query_rag(question_text: str) -> str:
    """
    Queries the RAG index and returns the most relevant textbook context
    as a single string to be injected into the LLM prompt.

    Args:
        question_text: The user's calculus question.

    Returns:
        A string of relevant textbook excerpts, or empty string if none found.
    """
    try:
        engine = _get_or_build_index()
        response = engine.query(question_text)

        if not response.source_nodes:
            logger.info("RAG returned no relevant context.")
            return ""

        # Combine the top-k retrieved chunks
        context_parts = []
        for i, node in enumerate(response.source_nodes, 1):
            score = getattr(node, "score", None)
            score_str = f" (relevance: {score:.2f})" if score else ""
            context_parts.append(
                f"--- Textbook Excerpt {i}{score_str} ---\n{node.get_text()}"
            )

        context = "\n\n".join(context_parts)
        logger.info(f"RAG returned {len(response.source_nodes)} relevant chunks.")
        return context

    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return ""


def ingest_pdfs():
    """
    Utility function to manually trigger PDF ingestion.
    Call this from a script or API endpoint to rebuild the index.
    """
    global _query_engine
    _query_engine = None  # Force rebuild

    try:
        import chromadb

        # Clear existing collection
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            chroma_client.delete_collection("calculus_docs")
            logger.info("Cleared existing ChromaDB collection.")
        except Exception:
            pass

        # Rebuild
        _get_or_build_index()
        logger.info("PDF ingestion complete!")
        return True

    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")
        return False
