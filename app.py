# app.py
import streamlit as st
from PIL import Image
import pytesseract
import tempfile
import asyncio
import whisper
import os
import sounddevice as sd
import soundfile as sf
import numpy as np

from orchestrator import orchestrate_query, get_market_brief
from agents.language_agent import generate_text_with_gemini

# Windows fix for pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Whisper model
whisper_model = whisper.load_model("base")

# Async wrapper
def run_async(coro_func, *args):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.ensure_future(coro_func(*args))
    else:
        return asyncio.run(coro_func(*args))

# Function to record from mic
def record_audio(duration=5, fs=44100):
    st.info(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        sf.write(f.name, audio, fs)
        return f.name

# UI
st.set_page_config(page_title="📈 AI Financial Advisor", layout="centered")
st.title("🤖 AI-Powered Financial Advisor")

st.markdown("""
Welcome to your smart financial assistant.

You can:
- 💬 Ask questions like: "What's the price of TSLA?"
- 🖼️ Upload images (screenshots, statements)
- 🎤 Upload or record voice questions
- 📊 Get daily market summary
""")

# --- Text Query ---
query = st.text_input("💬 Ask your financial question:", placeholder="e.g. What's the stock price of AAPL?")
if st.button("🔍 Run Query") and query:
    with st.spinner("Thinking..."):
        result = run_async(orchestrate_query, query)
        if asyncio.isfuture(result):
            result = asyncio.get_event_loop().run_until_complete(result)
    st.markdown("### 📢 Response:")
    st.success(result)

# --- Image Upload ---
st.markdown("### 🖼️ Upload Image for Analysis")
img_file = st.file_uploader("Upload a financial image (PNG/JPG)", type=["png", "jpg", "jpeg", "webp"])
if img_file:
    st.image(img_file, caption="Uploaded Image", use_column_width=True)
    image = Image.open(img_file)
    text = pytesseract.image_to_string(image)

    if text.strip():
        st.markdown("**📄 Extracted Text:**")
        st.code(text.strip())
        if st.button("🧠 Analyze Extracted Text"):
            with st.spinner("Analyzing..."):
                prompt = f"This is text extracted from a financial image. Please explain:\n\n{text}"
                summary = run_async(generate_text_with_gemini, prompt)
                if asyncio.isfuture(summary):
                    summary = asyncio.get_event_loop().run_until_complete(summary)
            st.success(summary)
    else:
        st.warning("No meaningful text found.")

# --- Audio Upload ---
st.markdown("### 🎤 Upload Voice Question (MP3/WAV)")
audio_file = st.file_uploader("Upload audio file", type=["mp3", "wav"])
if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_file.read())
        audio_path = tmp_audio.name
    with st.spinner("Transcribing..."):
        result = whisper_model.transcribe(audio_path)
        transcribed = result["text"]

    st.markdown("**🎧 Transcribed Text:**")
    st.code(transcribed.strip())

    if st.button("🧠 Analyze Voice Query"):
        with st.spinner("Processing..."):
            response = run_async(orchestrate_query, transcribed.strip())
            if asyncio.isfuture(response):
                response = asyncio.get_event_loop().run_until_complete(response)
        st.success(response)

# --- Live Mic Recording ---
st.markdown("### 🎙️ Speak Your Question")
if st.button("🔴 Record Now"):
    audio_path = record_audio(duration=5)
    with st.spinner("🎧 Transcribing your voice..."):
        result = whisper_model.transcribe(audio_path)
        spoken_text = result["text"]

    st.markdown("**📝 Transcribed Text:**")
    st.code(spoken_text.strip())

    if st.button("🤖 Run Voice Question"):
        with st.spinner("Getting your answer..."):
            response = run_async(orchestrate_query, spoken_text.strip())
            if asyncio.isfuture(response):
                response = asyncio.get_event_loop().run_until_complete(response)
        st.success(response)

# --- Market Brief ---
st.markdown("---")
st.markdown("### 📊 Market Summary")
if st.button("🧾 Show Market Brief"):
    with st.spinner("Gathering market updates..."):
        brief = run_async(get_market_brief)
        if asyncio.isfuture(brief):
            brief = asyncio.get_event_loop().run_until_complete(brief)
    st.info(brief)

# Footer
st.markdown("""
---
Built by Aryan Devaragari with 💡 AI, OCR, Whisper, and Finance APIs
""")
