# Finance Assistant

# Finance Bot: Multi-Agent Finance Assistant

This project implements a multi-agent finance assistant using FastAPI microservices, designed to provide financial insights, news, and analysis. It integrates various AI components including large language models (Gemini), voice processing (Whisper for STT, gTTS for TTS), and a RAG pipeline.

## Features

* **API Agent:** Fetches real-time stock data and historical information using Alpha Vantage.
* **Scraping Agent:** Crawls financial news from a mock source. (For a real application, this would be extended to more robust sources like SEC filings or specific news APIs).
* **Retriever Agent:** Implements a Retrieval-Augmented Generation (RAG) pipeline using FAISS for efficient document similarity search and `langchain` with Gemini embeddings.
* **Analysis Agent:** Performs basic financial calculations and risk assessments.
* **Language Agent:** Interacts with the Gemini LLM for generating insightful responses based on retrieved information.
* **Voice Agent:** Handles Speech-to-Text (STT) using Whisper and Text-to-Speech (TTS) using gTTS for natural voice interaction.
* **Orchestrator:** Routes user queries to the appropriate agents and synthesizes responses.
* **Streamlit Frontend:** A user-friendly web interface with voice and text input, and potential for data visualizations.
* **Scheduled Automation:** (Conceptual/Placeholder) Designed to trigger daily market briefs.
* **Fallback Logic:** Provides graceful degradation if specific information retrieval fails.
* **Visualizations:** Integrated into the Streamlit frontend for portfolio insights and stock graphs.

## Project Structure


finance_bot/
├── agents/                 # Individual microservices for each agent
│   ├── init.py
│   ├── api_agent.py        # Alpha Vantage integration
│   ├── scraping_agent.py   # Web scraping for news
│   ├── retriever_agent.py  # RAG pipeline with FAISS + Gemini embeddings
│   ├── analysis_agent.py   # Financial calculations
│   ├── language_agent.py   # Gemini LLM integration
│   └── voice_agent.py      # Whisper (STT) + gTTS (TTS)
├── orchestrator.py         # Main routing and query handling logic
├── backend.py              # FastAPI main application, integrates all agent routers
├── .env                    # Environment variables for API keys
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build file for containerization
├── README.md               # Project overview and setup instructions
├── docs/                   # Documentation folder
│   └── ai_tool_usage.md    # Logs of AI tool usage during generation
└── streamlit_app/          # Streamlit frontend application
└── app.py


## Setup and Running

Follow these steps to set up and run the Finance Bot.

### 1. Clone the Repository (Simulated)

In a real scenario, you would clone the repository. For this output, manually create the `finance_bot` directory and all subdirectories, then populate them with the provided code.

```bash
mkdir finance_bot
cd finance_bot
# Create agents/docs/streamlit_app subdirectories
mkdir agents docs streamlit_app
