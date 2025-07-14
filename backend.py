from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn
import io
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment variables
load_dotenv()

# Debug statements
print(f"DEBUG: ALPHA_VANTAGE_API_KEY loaded: {os.getenv('ALPHA_VANTAGE_API_KEY') is not None}")
print(f"DEBUG: GEMINI_API_KEY loaded: {os.getenv('GEMINI_API_KEY') is not None}")
print(f"DEBUG: Current Working Directory (where .env is expected): {os.getcwd()}")

# Import agent routers
from agents.api_agent import router as api_router
from agents.scraping_agent import router as scraping_router
from agents.retriever_agent import router as retriever_router
from agents.analysis_agent import router as analysis_router
from agents.language_agent import router as language_router
from agents.voice_agent import router as voice_router

# Orchestrator logic
from orchestrator import orchestrate_query, get_market_brief

app = FastAPI(
    title="Finance Bot Backend",
    description="Multi-agent finance assistant with FastAPI microservices."
)

# Include agent routers
app.include_router(api_router, prefix="/api_agent", tags=["API Agent"])
app.include_router(scraping_router, prefix="/scraping_agent", tags=["Scraping Agent"])
app.include_router(retriever_router, prefix="/retriever_agent", tags=["Retriever Agent"])
app.include_router(analysis_router, prefix="/analysis_agent", tags=["Analysis Agent"])
app.include_router(language_router, prefix="/language_agent", tags=["Language Agent"])
app.include_router(voice_router, prefix="/voice_agent", tags=["Voice Agent"])

# Scheduler
scheduler = AsyncIOScheduler()

async def scheduled_market_brief():
    print("\n[Scheduler] Generating daily market brief...")
    brief = await get_market_brief()
    print(f"[Scheduler] Market Brief:\n{brief}\n")
    app.state.last_market_brief = brief

@app.on_event("startup")
async def startup_event():
    trigger = CronTrigger(minute='*/5')  # Every 5 mins for testing
    scheduler.add_job(scheduled_market_brief, trigger)
    scheduler.start()
    print("Scheduler started.")
    print("Retriever Agent's FAISS index initialization will run automatically via its startup event.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("Scheduler shutdown.")

# --- Main JSON Query Handler ---
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_finance_bot(request: QueryRequest):
    try:
        response_text = await orchestrate_query(request.query)
        return JSONResponse({"response": response_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Voice-based Query Handler ---
@app.post("/ask_voice")
async def ask_finance_bot_voice(audio_file: UploadFile = File(...)):
    try:
        audio_content = await audio_file.read()
        headers = {'Content-Type': 'audio/webm'}
        audio_io = io.BytesIO(audio_content)
        audio_io.name = audio_file.filename

        from agents.voice_agent import transcribe_audio
        text_query = await transcribe_audio(audio_io)

        if not text_query:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")

        response_text = await orchestrate_query(text_query)

        from agents.voice_agent import text_to_speech
        audio_response_bytes = await text_to_speech(response_text)

        return StreamingResponse(io.BytesIO(audio_response_bytes), media_type="audio/mpeg")

    except Exception as e:
        print(f"Error in ask_voice: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# --- Scheduled Market Brief Endpoint ---
@app.get("/get_market_brief")
async def get_current_market_brief():
    brief = getattr(app.state, 'last_market_brief', "No market brief available yet. It runs on a schedule.")
    return JSONResponse({"market_brief": brief})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
