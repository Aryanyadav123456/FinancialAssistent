# agents/retriever_agent.py

from fastapi import APIRouter, HTTPException
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
import time
from typing import Tuple, List

# ✅ Fix OpenMP duplicate library issue
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Load environment variables
load_dotenv()

router = APIRouter()

# --- Load Gemini Embeddings ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file for Retriever Agent.")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)

# Global FAISS store
faiss_vectorstore = None

# --- Dummy Docs for FAISS Index ---
DUMMY_FINANCIAL_DOCS = [
    "Federated learning is a machine learning approach that trains an algorithm across multiple decentralized edge devices or servers...",
    "Blockchain technology, fundamentally a decentralized, distributed ledger...",
    "Quantum computing in finance is an emerging field...",
    "The concept of 'Efficient Market Hypothesis' suggests that financial markets are 'informationally efficient'...",
    "Algorithmic trading uses computer programs to execute trades...",
    "Risk management in finance involves identifying, analyzing, and mitigating financial risks...",
    "ESG investing refers to a set of standards for a company’s operations...",
    "Diversification is a strategy employed to minimize risk by investing in a variety of assets..."
]

# --- FAISS Index Creation ---
async def create_faiss_index(documents: List[str]):
    """
    Create or update FAISS index from a list of documents.
    """
    print("[Retriever Agent] Creating FAISS index...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text("\n".join(documents))

    global faiss_vectorstore
    if faiss_vectorstore is None:
        faiss_vectorstore = FAISS.from_texts(texts, embeddings)
        print("[Retriever Agent] FAISS index created.")
    else:
        faiss_vectorstore.add_texts(texts)
        print("[Retriever Agent] FAISS index updated.")

# --- Main RAG Function ---
async def retrieve_info_from_rag(query: str, k: int = 2) -> Tuple[str, float]:
    """
    Retrieve top-k docs from FAISS index for a query.
    """
    global faiss_vectorstore
    if faiss_vectorstore is None:
        await create_faiss_index(DUMMY_FINANCIAL_DOCS)

    print(f"[Retriever Agent] Retrieving for query: '{query}'")
    start = time.time()

    try:
        docs_with_scores = faiss_vectorstore.similarity_search_with_score(query, k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS similarity search failed: {str(e)}")

    if not docs_with_scores:
        return "No relevant documents found.", 0.0

    contents = []
    scores = []

    for doc, score in docs_with_scores:
        contents.append(doc.page_content)
        confidence = max(0, 1 - (score / 1.0))  # Heuristic
        scores.append(confidence)
        print(f"  - Match: '{doc.page_content[:50]}...' | Score: {score:.4f} | Confidence: {confidence:.2f}")

    elapsed = time.time() - start
    print(f"[Retriever Agent] Retrieval completed in {elapsed:.2f} seconds.")

    avg_conf = sum(scores) / len(scores)
    return "\n\n".join(contents), avg_conf

# --- FastAPI Events ---
@router.on_event("startup")
async def on_startup():
    """Initialize FAISS on app startup."""
    await create_faiss_index(DUMMY_FINANCIAL_DOCS)

# --- Endpoints ---
@router.post("/retrieve")
async def retrieve_data(query: str):
    """
    Main RAG retrieval endpoint.
    """
    print(f"[Retriever Agent] /retrieve hit with query: '{query}'")
    try:
        content, confidence = await retrieve_info_from_rag(query)
        return {"content": content, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_document")
async def add_document_to_index(document: str):
    """
    Add new content to the FAISS index.
    """
    print(f"[Retriever Agent] Adding document: '{document[:50]}...'")
    await create_faiss_index([document])
    return {"message": "Document added to index."}
