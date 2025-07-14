from fastapi import APIRouter, HTTPException, Body
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

router = APIRouter()

BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# --- API Interaction Functions ---
async def fetch_alpha_vantage_data(function: str, symbol: str, **kwargs):
    """
    Generic function to fetch data from Alpha Vantage API.
    """
    if not ALPHA_VANTAGE_API_KEY:
        raise HTTPException(status_code=500, detail="Alpha Vantage API key not set in environment.")

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
        **kwargs
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            print(f"Alpha Vantage API Error: {data['Error Message']}")
            raise HTTPException(status_code=400, detail=data["Error Message"])
        elif "Note" in data:
            print(f"Alpha Vantage API Note (Rate Limit?): {data['Note']}")
            return {}  # Return empty to signify no data yet
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request to Alpha Vantage failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Alpha Vantage: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

async def get_stock_quote(ticker: str):
    return await fetch_alpha_vantage_data("GLOBAL_QUOTE", ticker)

async def get_historical_data(ticker: str, outputsize: str = "compact"):
    return await fetch_alpha_vantage_data("TIME_SERIES_DAILY", ticker, outputsize=outputsize)

# --- FastAPI Endpoints ---
@router.get("/quote/{ticker}")
async def read_stock_quote(ticker: str):
    print(f"[API Agent] Fetching quote for {ticker}")
    quote = await get_stock_quote(ticker)
    return quote

@router.get("/historical/{ticker}")
async def read_historical_data(ticker: str, outputsize: str = "compact"):
    print(f"[API Agent] Fetching historical data for {ticker} (outputsize: {outputsize})")
    data = await get_historical_data(ticker, outputsize)
    return data

@router.post("/stock_price")
async def get_stock_price_post(payload: dict = Body(...)):
    """
    POST endpoint to get current stock price in simplified format.
    Expected body: { "symbol": "AAPL" }
    """
    symbol = payload.get("symbol")
    if not symbol:
        raise HTTPException(status_code=400, detail="Missing 'symbol' in request body.")

    print(f"[API Agent] Fetching real-time price for {symbol}")
    data = await get_stock_quote(symbol)

    try:
        price = data["Global Quote"]["05. price"]
    except KeyError:
        raise HTTPException(status_code=500, detail="Failed to extract price from API response.")

    return {"symbol": symbol.upper(), "price": price}
