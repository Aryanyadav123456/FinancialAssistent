# agents/language_agent.py
from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import asyncio

load_dotenv() # Load environment variables

router = APIRouter()

# Initialize Gemini LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file for Language Agent.")

# UPDATED: Changed model to gemini-2.0-flash
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

async def generate_text_with_gemini(prompt: str) -> str:
    """
    Generates text using the Gemini LLM.
    """
    print(f"[Language Agent] Generating text with prompt: '{prompt[:100]}...'")
    try:
        # Use invoke for a single turn conversation
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate text with Gemini: {e}")

# --- FastAPI Endpoint ---
@router.post("/generate")
async def generate_text(prompt: str):
    """
    Endpoint to generate text using the Gemini LLM.
    """
    print(f"[Language Agent] Request received for text generation.")
    generated_text = await generate_text_with_gemini(prompt)
    return {"generated_text": generated_text}
