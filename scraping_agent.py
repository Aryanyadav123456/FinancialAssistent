# agents/scraping_agent.py
from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
import asyncio

router = APIRouter()

# Mock/simplified news data for demonstration
MOCK_FINANCIAL_NEWS = {
    "market": [
        "Global markets show mixed signals as inflation concerns persist.",
        "Tech stocks lead rally; S&P 500 hits new high.",
        "Oil prices surge amidst geopolitical tensions.",
        "Central banks hint at potential interest rate changes."
    ],
    "company": {
        "AAPL": [
            "Apple announces record quarterly earnings, driven by iPhone sales.",
            "Analysts raise price targets for AAPL after new product unveiling.",
            "Apple faces antitrust scrutiny in Europe."
        ],
        "GOOGL": [
            "Google invests heavily in AI research and development.",
            "Alphabet beats revenue estimates, cloud growth impresses.",
            "Google's ad business shows resilience despite market slowdown."
        ],
        "MSFT": [
            "Microsoft expands cloud services, invests in AI partnerships.",
            "Windows 12 rumors surface ahead of major Microsoft event.",
            "Microsoft acquires leading gaming studio for undisclosed sum."
        ]
    },
    "default": [
        "Top financial analysts share their 2024 predictions.",
        "Understanding the basics of personal finance and investment.",
        "Cryptocurrency market experiences high volatility.",
        "Real estate market trends: What to expect next quarter."
    ]
}

async def get_financial_news_mock(query_term: str = "market"):
    """
    Mock function to simulate crawling financial news.
    In a real scenario, this would involve actual web scraping or API calls.
    For demonstration, it returns predefined news based on query_term.
    """
    print(f"[Scraping Agent] Mocking news search for: {query_term}")
    query_lower = query_term.lower()

    if any(ticker in query_lower for ticker in ["aapl", "googl", "msft"]):
        for ticker_key, news_list in MOCK_FINANCIAL_NEWS["company"].items():
            if ticker_key.lower() in query_lower:
                return news_list
    elif "market" in query_lower:
        return MOCK_FINANCIAL_NEWS["market"]
    
    return MOCK_FINANCIAL_NEWS["default"]

# --- FastAPI Endpoint ---
@router.get("/news")
async def read_financial_news(query_term: str = "market"):
    """
    Endpoint to get financial news headlines.
    Uses mock data or a very simple scrape.
    """
    print(f"[Scraping Agent] Request received for news with term: '{query_term}'")
    
    # Attempt a very basic scrape for a generic finance news site
    # This is highly fragile and for demonstration purposes only.
    # A real scraper would need robust error handling, anti-blocking measures, and specific selectors.
    try:
        # Corrected: Ensure no extra characters from Markdown link
        response = requests.get("https://www.cnbc.com/finance/")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        # Example: Find top news headlines, specific to CNBC's current structure
        # This will likely break as websites change.
        for h in soup.find_all('a', class_='Card-title'): # Example class
            if h.text.strip():
                headlines.append(h.text.strip())
            if len(headlines) >= 5: # Limit to top 5
                break
        
        if headlines:
            print("[Scraping Agent] Successfully scraped some headlines.")
            return headlines
        else:
            print("[Scraping Agent] No headlines found via basic scrape. Using mock data.")
            return await get_financial_news_mock(query_term)
    except requests.exceptions.RequestException as e:
        print(f"[Scraping Agent] Basic scrape failed: {e}. Falling back to mock data.")
        return await get_financial_news_mock(query_term)
    except Exception as e:
        print(f"[Scraping Agent] Error during scraping or parsing: {e}. Falling back to mock data.")
        return await get_financial_news_mock(query_term)
