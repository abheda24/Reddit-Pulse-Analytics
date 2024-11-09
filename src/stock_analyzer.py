import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

class StockDataAnalyzer:
    """
    A class for fetching and analyzing stock market data.
    """
    
    def __init__(self):
        """Initialize the stock analyzer."""
        pass

    @lru_cache(maxsize=100)
    def get_stock_data(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch stock data using yfinance.
        
        Args:
            symbol: Stock symbol
            period: Time period to fetch
            interval: Data interval
            
        Returns:
            DataFrame containing stock data
        """
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return pd.DataFrame()
                
            logger.info(f"Successfully fetched stock data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def calculate_metrics(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate key stock metrics.
        
        Args:
            df: DataFrame containing stock data
            
        Returns:
            Dictionary of calculated metrics
        """
        if df.empty:
            return {}
            
        try:
            metrics = {
                'daily_returns': df['Close'].pct_change(),
                'volatility': df['Close'].pct_change().std() * np.sqrt(252),
                'avg_volume': df['Volume'].mean(),
                'price_change': (
                    df['Close'].iloc[-1] - df['Close'].iloc[0]
                ) / df['Close'].iloc[0]
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating stock metrics: {str(e)}")
            return {}

    def analyze_correlation(
        self, 
        symbol1: str, 
        symbol2: str, 
        period: str = "1mo"
    ) -> float:
        """
        Calculate correlation between two stocks.
        
        Args:
            symbol1: First stock symbol
            symbol2: Second stock symbol
            period: Time period for analysis
            
        Returns:
            Correlation coefficient
        """
        try:
            df1 = self.get_stock_data(symbol1, period)
            df2 = self.get_stock_data(symbol2, period)
            
            if df1.empty or df2.empty:
                return 0.0
                
            # Calculate correlation
            correlation = df1['Close'].corr(df2['Close'])
            return correlation
            
        except Exception as e:
            logger.error(
                f"Error calculating correlation between {symbol1} and {symbol2}: {str(e)}"
            )
            return 0.0