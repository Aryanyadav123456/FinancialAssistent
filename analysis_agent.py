# agents/analysis_agent.py
from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import asyncio
from typing import List, Dict, Any

# Mock historical data for analysis if API agent is not used or fails
MOCK_HISTORICAL_PRICES = {
    "AAPL": pd.Series([150, 152, 151, 155, 153, 158, 160], index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'])),
    "GOOGL": pd.Series([100, 101, 99, 103, 102, 105, 104], index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'])),
    "MSFT": pd.Series([200, 203, 201, 205, 204, 208, 210], index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'])),
    "TSLA": pd.Series([250, 245, 260, 255, 270, 265, 280], index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'])),
    "NVDA": pd.Series([300, 310, 305, 320, 315, 330, 325], index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'])),
}


router = APIRouter()

# --- Analysis Functions ---
async def calculate_returns(prices: pd.Series) -> float:
    """Calculates daily percentage returns."""
    return (prices.pct_change().dropna() * 100).mean()

async def calculate_volatility(prices: pd.Series) -> float:
    """Calculates annualized volatility (standard deviation of daily returns)."""
    daily_returns = prices.pct_change().dropna()
    annualized_vol = daily_returns.std() * np.sqrt(252) * 100 # Assuming 252 trading days
    return annualized_vol

async def assess_risk(volatility: float) -> str:
    """Provides a qualitative assessment of risk based on volatility."""
    if volatility > 30:
        return "High Risk"
    elif volatility > 15:
        return "Medium Risk"
    else:
        return "Low Risk"

async def get_mock_prices_for_ticker(ticker: str) -> pd.Series:
    """
    Retrieves mock historical prices for a given ticker.
    In a real scenario, this would integrate with the API Agent.
    """
    if ticker.upper() in MOCK_HISTORICAL_PRICES:
        return MOCK_HISTORICAL_PRICES[ticker.upper()]
    else:
        # Fallback to a generic pattern if ticker not in mock data
        dates = pd.to_datetime(pd.date_range(start='2023-01-01', periods=7, freq='D'))
        return pd.Series(np.linspace(100, 110, 7) + np.random.randn(7)*2, index=dates)


async def analyze_risk_volatility_returns(tickers: List[str]) -> Dict[str, Any]:
    """
    Performs basic risk, volatility, and return analysis for given tickers.
    """
    print(f"[Analysis Agent] Analyzing tickers: {tickers}")
    results = {}
    for ticker in tickers:
        prices = await get_mock_prices_for_ticker(ticker) # Use mock prices
        
        if prices.empty or len(prices) < 2:
            results[ticker] = "Insufficient data for analysis."
            continue

        avg_returns = await calculate_returns(prices)
        volatility = await calculate_volatility(prices)
        risk_assessment = await assess_risk(volatility)

        results[ticker] = {
            "Average Daily Returns (%):": f"{avg_returns:.2f}",
            "Annualized Volatility (%):": f"{volatility:.2f}",
            "Risk Assessment": risk_assessment
        }
    return results

# --- FastAPI Endpoint ---
@router.post("/analyze")
async def perform_analysis(tickers: List[str]):
    """
    Endpoint to perform financial analysis on a list of tickers.
    """
    print(f"[Analysis Agent] Request received for analysis on: {tickers}")
    analysis_results = await analyze_risk_volatility_returns(tickers)
    return analysis_results
