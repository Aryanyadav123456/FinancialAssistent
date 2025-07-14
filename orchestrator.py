# orchestrator.py
import re
from typing import Dict, Any

# Load keys from gemini.txt
def load_api_keys_from_file(filepath="gemini.txt"):
    try:
        with open(filepath, "r") as f:
            lines = f.read().splitlines()
        keys = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                keys[key.strip()] = value.strip()
        return keys
    except Exception as e:
        raise RuntimeError(f"Error loading API keys from {filepath}: {e}")

API_KEYS = load_api_keys_from_file()
ALPHA_VANTAGE_API_KEY = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
GEMINI_API_KEY = API_KEYS.get("GEMINI_API_KEY")

# Agents
from agents.api_agent import get_stock_quote, get_historical_data
from agents.scraping_agent import get_financial_news_mock
from agents.retriever_agent import retrieve_info_from_rag
from agents.analysis_agent import analyze_risk_volatility_returns
from agents.language_agent import generate_text_with_gemini

# ---------------- MAIN QUERY LOGIC ---------------- #

async def orchestrate_query(query: str) -> str:
    query_lower = query.lower()
    response = ""

    print(f"\n[Orchestrator] Received query: '{query}'")

    # ✅ Fixed regex: ticker properly captured
    stock_match = re.search(r'(price|quote|stock|performance|historical).*?\b([A-Z]{1,5})\b', query)
    if stock_match:
        ticker = stock_match.group(2).upper()

        # Historical
        if "historical" in query_lower or "performance" in query_lower:
            print(f"[Orchestrator] Routing to API Agent for historical data on {ticker}")
            data = await get_historical_data(ticker)
            if data.get("Note"):
                return data["Note"]
            if data.get("Information"):
                return data["Information"]
            if data and data.get("Time Series (Daily)"):
                latest_date = list(data["Time Series (Daily)"].keys())[0]
                latest_close = data["Time Series (Daily)"][latest_date]["4. close"]
                dates = list(data["Time Series (Daily)"].keys())[:7]
                prices = [float(data["Time Series (Daily)"][d]["4. close"]) for d in dates if d in data["Time Series (Daily)"]]
                if len(prices) > 1:
                    returns = (prices[0] - prices[-1]) / prices[-1] * 100
                    response = (f"Historical performance for {ticker}: Latest close on {latest_date} was {latest_close}. "
                                f"Over the last {len(prices)} days, it changed by {returns:.2f}%.")
                else:
                    response = f"Latest close for {ticker} on {latest_date} was {latest_close}."
            else:
                response = f"⚠️ Could not retrieve historical data for {ticker}."
            return response

        # Real-time quote
        else:
            print(f"[Orchestrator] Routing to API Agent for live quote on {ticker}")
            data = await get_stock_quote(ticker)
            print("[DEBUG] Alpha Vantage quote response:", data)

            if data.get("Note"):
                return data["Note"]
            if data.get("Information"):
                return data["Information"]
            if data and "Global Quote" in data and data["Global Quote"]:
                quote_info = data["Global Quote"]
                response = (
                    f"📈 {ticker} Stock Quote:\n"
                    f"Open: {quote_info.get('02. open')}\n"
                    f"High: {quote_info.get('03. high')}\n"
                    f"Low: {quote_info.get('04. low')}\n"
                    f"Price: {quote_info.get('05. price')}\n"
                    f"Volume: {quote_info.get('06. volume')}\n"
                    f"Last Trading Day: {quote_info.get('07. latest trading day')}"
                )
            else:
                response = f"⚠️ Could not retrieve live quote for {ticker}."
            return response

    # News
    elif "news" in query_lower or "headlines" in query_lower or "filings" in query_lower:
        print("[Orchestrator] Routing to Scraping Agent for news.")
        news_query_term = query_lower.replace("news about", "").replace("latest news on", "").strip()
        news = await get_financial_news_mock(news_query_term)
        if news:
            response = "📰 Latest News:\n" + "\n".join([f"- {n}" for n in news])
        else:
            response = "⚠️ Could not retrieve financial news at this time."
        return response

    # Risk/Analysis
    elif any(term in query_lower for term in ["analyze", "risk", "volatility", "returns", "portfolio"]):
        print("[Orchestrator] Routing to Analysis Agent.")
        tickers_for_analysis = ["AAPL", "GOOGL"]
        analysis_result = await analyze_risk_volatility_returns(tickers_for_analysis)
        response = f"📊 Financial Analysis for {', '.join(tickers_for_analysis)}:\n{analysis_result}"
        return response

    # General Knowledge via Retriever + LLM
    elif any(term in query_lower for term in ["explain", "what is", "tell me about", "define"]):
        print(f"[Orchestrator] Routing to Retriever Agent for query: '{query}'")
        retrieved_content, confidence_score = await retrieve_info_from_rag(query)
        if confidence_score < 0.7:
            print(f"[Orchestrator] Low RAG confidence ({confidence_score:.2f}), fallback to Gemini.")
            response = await generate_text_with_gemini(f"Explain this concept: {query}")
            return f"I couldn't find very specific info, but here's what I know:\n\n{response}"
        else:
            print("[Orchestrator] Passing RAG context to Gemini.")
            prompt = f"Explain this based on context:\n\n{retrieved_content}\n\nUser asked: {query}"
            response = await generate_text_with_gemini(prompt)
            return f"📘 Here's what I found:\n\n{response}"

    # Default fallback
    else:
        print("[Orchestrator] Default route to Gemini.")
        response = await generate_text_with_gemini(f"User asked: {query}. Please respond as a financial assistant.")
        return response


# ---------------- MARKET BRIEF ---------------- #

async def get_market_brief() -> str:
    print("[Orchestrator] Generating Market Brief...")
    brief_parts = []

    # Major Index ETFs
    tickers = ["SPY", "QQQ", "DIA"]
    for ticker in tickers:
        data = await get_stock_quote(ticker)
        if data.get("Note"):
            return data["Note"]
        if data and "Global Quote" in data:
            price = data["Global Quote"].get("05. price", "N/A")
            change = data["Global Quote"].get("09. change", "N/A")
            brief_parts.append(f"{ticker}: ${price} (Change: {change})")
        else:
            brief_parts.append(f"{ticker}: Quote unavailable.")

    # News
    news = await get_financial_news_mock("market")
    if news:
        brief_parts.append("\n🗞️ News:")
        brief_parts += [f"- {h}" for h in news[:3]]

    # Summary via LLM
    prompt = "Summarize this market brief:\n" + "\n".join(brief_parts)
    summary = await generate_text_with_gemini(prompt)
    return summary
