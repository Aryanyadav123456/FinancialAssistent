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
📈 AI-Powered Financial Assistant
Welcome to your open-source, multi-agent finance assistant that delivers daily spoken market briefs, analyzes uploaded documents and images, and answers financial queries via voice or text!

🚀 Features
 Ask in natural language (text or voice)
 Upload images (financial statements, screenshots) for analysis
 Get live stock prices from AlphaVantage/Yahoo Finance
 Retrieval-Augmented Generation (RAG) over financial documents
 Daily market summary with voice output

🗺️ Architecture Overview
This system uses modular agents orchestrated via FastAPI microservices:

🎛️ Agents
Agent	Description	Tools/Frameworks
API Agent	Fetches live market data	AlphaVantage / Yahoo Finance, FastAPI
Scraping Agent	Crawls earnings filings (SEC etc.)	BeautifulSoup, FastAPI
Retriever Agent	Embeds and queries documents	LangChain, FAISS
Analysis Agent	Summarizes risk exposure & earnings surprises	LangChain, OpenAI, Pandas
Language Agent	Synthesizes narrative	LangChain RetrieverQA, OpenAI
Voice Agent	Speech-to-text and text-to-speech	Whisper, gTTS

🗂️ Directories
Copy
Edit
finance_assistant/
├── agents/
│   ├── api_agent.py
│   ├── scraping_agent.py
│   ├── retriever_agent.py
│   ├── analysis_agent.py
│   ├── language_agent.py
│   └── voice_agent.py
├── orchestrator/
│   └── orchestrator.py
├── streamlit_app/
│   └── streamlit_app.py
├── data_ingestion/
│   └── sec_scraper.py
├── notebooks/
│   └── Finance_Assistant_Notebook.ipynb
├── requirements.txt
├── Dockerfile
├── README.md
└── docs/
    └── ai_tool_usage.md
📸 User Interface (Example)

Your Streamlit app supports:

💬 Text questions

📸 Image upload for OCR/analysis

🎤 Voice upload for STT

📈 Spoken market briefs

⚙️ Setup & Installation
1️⃣ Clone the Repo
bash
Copy
Edit
git clone https://github.com/yourusername/finance-assistant.git
cd finance-assistant
2️⃣ Install Requirements
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Set Environment Variables
Create a .env file:

ini
Copy
Edit
OPENAI_API_KEY=your-key
ALPHAVANTAGE_API_KEY=your-key
4️⃣ Run Microservices
Each agent is a FastAPI service:

bash
Copy
Edit
uvicorn agents.api_agent:app --reload --port 8001
uvicorn agents.scraping_agent:app --reload --port 8002
...
uvicorn orchestrator.orchestrator:app --reload --port 9000
5️⃣ Run Streamlit App
bash
Copy
Edit
streamlit run streamlit_app/streamlit_app.py
🌐 Deployment
✅ Dockerfile included for containerized deployment.
✅ Supports Render, Railway, or Streamlit Community Cloud.
✅ You can use ngrok for local tunneling:

 Use Case: Morning Market Brief
Example query:

“What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?”

Example response:

“Today, your Asia tech allocation is 22% of AUM, up from 18% yesterday. TSMC beat estimates by 4%, Samsung missed by 2%. Regional sentiment is neutral with a cautionary tilt due to rising yields.”

📑 Documentation
✅ /docs/ai_tool_usage.md — Logs of all prompts, LLM parameters
✅ /notebooks/ — Exploratory pipelines for agents and retrieval
✅ /agents/ — Modular FastAPI microservices
✅ /streamlit_app/ — User-friendly front-end

🧠 Tech Stack
LangChain for Retrieval-Augmented Generation (RAG)

FAISS for vector storage

OpenAI for LLM & embeddings

BeautifulSoup for scraping

Whisper for speech-to-text

gTTS for text-to-speech

CrewAI / LangGraph for agent orchestration

FastAPI for microservices

Streamlit for UI

📌 License
Open-source, MIT License.

🙌 Acknowledgements
OpenAI

AlphaVantage

Whisper

LangChain

Streamlit
