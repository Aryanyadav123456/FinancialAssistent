# agents/voice_agent.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from gtts import gTTS
import io
import asyncio
from transformers import pipeline
import torch
import soundfile as sf
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables

router = APIRouter()

# --- Speech-to-Text (STT) with Whisper ---
# Initialize Whisper pipeline. Using a smaller model for faster inference and smaller Docker image.
# On first run, this will download the model.
# Ensure you have enough RAM/CPU for this or consider using a hosted API for Whisper in production.
try:
    print("[Voice Agent] Initializing Whisper STT model (openai/whisper-tiny)... This may take a moment.")
    # Set cache directory for models if needed, e.g., in Dockerfile/env
    # os.environ['HF_HOME'] = '/app/.cache/huggingface'
    stt_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=0 if torch.cuda.is_available() else -1)
    print("[Voice Agent] Whisper STT model initialized.")
except Exception as e:
    print(f"Error initializing Whisper model: {e}")
    stt_pipeline = None # Set to None if initialization fails

async def transcribe_audio(audio_file_stream: io.BytesIO) -> str:
    """
    Transcribes an audio stream to text using Whisper.
    Expects audio_file_stream to be a BytesIO object containing audio data.
    """
    if stt_pipeline is None:
        raise HTTPException(status_code=500, detail="Whisper STT model not initialized.")

    print("[Voice Agent] Transcribing audio to text...")
    try:
        # Save BytesIO to a temporary file for Whisper pipeline if needed,
        # or convert to numpy array which pipeline can often handle.
        # sf.read can read directly from BytesIO
        audio_data, samplerate = sf.read(audio_file_stream)
        
        # Ensure audio data is mono for Whisper if it's stereo
        if len(audio_data.shape) > 1 and audio_data.shape[1] == 2:
            audio_data = audio_data.mean(axis=1) # Convert to mono
        
        # The pipeline expects a dictionary with "sampling_rate" and "raw" audio data
        audio_input = {"sampling_rate": samplerate, "raw": audio_data}
        
        # Run inference
        prediction = stt_pipeline(audio_input)
        transcribed_text = prediction["text"]
        print(f"[Voice Agent] Transcribed text: '{transcribed_text}'")
        return transcribed_text
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Audio transcription failed: {e}")

# --- Text-to-Speech (TTS) with gTTS ---
async def text_to_speech(text: str) -> bytes:
    """
    Converts text to speech (MP3 bytes) using gTTS.
    """
    print(f"[Voice Agent] Converting text to speech: '{text[:100]}...'")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        print("[Voice Agent] Text converted to speech.")
        return audio_fp.getvalue()
    except Exception as e:
        print(f"Error during text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {e}")

# --- FastAPI Endpoints ---
@router.post("/stt")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Endpoint to convert speech audio to text.
    """
    print(f"[Voice Agent] STT request received for file: {audio_file.filename}")
    audio_content = await audio_file.read()
    audio_stream = io.BytesIO(audio_content)
    audio_stream.name = audio_file.filename # gTTS expects a name attribute for some internal uses

    transcribed_text = await transcribe_audio(audio_stream)
    return {"text": transcribed_text}

@router.post("/tts")
async def text_to_speech_endpoint(text: str):
    """
    Endpoint to convert text to speech audio (MP3).
    """
    print(f"[Voice Agent] TTS request received for text: '{text[:50]}...'")
    audio_bytes = await text_to_speech(text)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")

