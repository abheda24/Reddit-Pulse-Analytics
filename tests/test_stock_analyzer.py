import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.stock_analyzer import StockDataAnalyzer

@pytest.fixture
def sample_stock_data():
    """Fixture providing sample stock price data."""
    dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'Open': [100, 101, 102, 101, 103],
        'High': [102, 103, 104, 103, 105],
        'Low': [99, 100, 101, 100, 102],
        'Close': [101, 102, 103, 102, 104],
        'Volume': [1000, 1100, 1200, 1100, 1300]
    }, index=dates)

def test_stock_analyzer_initialization():
    """Test stock analyzer initialization."""
    analyzer = StockDataAnalyzer()
    assert analyzer is not None

def test_get_stock_data(mocker):
    """Test fetching stock data."""
    analyzer = StockDataAnalyzer()
    
    # Mock yfinance Ticker
    mock_ticker = mocker.Mock()
    mock_ticker.history.return_value = pd.DataFrame({
        'Open': [100],
        'High': [101],
        'Low': [99],
        'Close': [100.5],
        'Volume': [1000]
    })
    
    mocker.patch('yfinance.Ticker', return_value=mock_ticker)
    
    df = analyzer.get_stock_data('AAPL', period='1d')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])

def test_calculate_metrics(sample_stock_data):
    """Test calculation of stock metrics."""
    analyzer = StockDataAnalyzer()
    metrics = analyzer.calculate_metrics(sample_stock_data)
    
    assert isinstance(metrics, dict)
    assert 'daily_returns' in metrics
    assert 'volatility' in metrics
    assert 'avg_volume' in metrics
    assert 'price_change' in metrics
    
    # Test metric values
    assert isinstance(metrics['daily_returns'], pd.Series)
    assert isinstance(metrics['volatility'], float)
    assert metrics['avg_volume'] == sample_stock_data['Volume'].mean()
    expected_price_change = (
        sample_stock_data['Close'].iloc[-1] - sample_stock_data['Close'].iloc[0]
    ) / sample_stock_data['Close'].iloc[0]
    assert np.isclose(metrics['price_change'], expected_price_change)

def test_analyze_correlation(mocker):
    """Test correlation analysis between stocks."""
    analyzer = StockDataAnalyzer()
    
    # Create sample data for two stocks
    sample_data = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104]
    })
    
    # Mock yfinance for both stocks
    mock_ticker = mocker.Mock()
    mock_ticker.history.return_value = sample_data
    mocker.patch('yfinance.Ticker', return_value=mock_ticker)
    
    correlation = analyzer.analyze_correlation('AAPL', 'MSFT', period='1w')
    assert isinstance(correlation, float)
    assert -1 <= correlation <= 1  # Correlation should be between -1 and 1

def test_empty_data_handling():
    """Test handling of empty data."""
    analyzer = StockDataAnalyzer()
    
    empty_df = pd.DataFrame()
    metrics = analyzer.calculate_metrics(empty_df)
    assert metrics == {}  # Should return empty dict for empty data

def test_error_handling(mocker):
    """Test error handling in stock analysis."""
    analyzer = StockDataAnalyzer()
    
    # Mock yfinance to raise an exception
    mock_ticker = mocker.Mock()
    mock_ticker.history.side_effect = Exception("API Error")
    mocker.patch('yfinance.Ticker', return_value=mock_ticker)
    
    # Should return empty DataFrame on error
    df = analyzer.get_stock_data('INVALID')
    assert isinstance(df, pd.DataFrame)
    assert df.empty

def test_invalid_stock_correlation(mocker):
    """Test correlation analysis with invalid stock symbols."""
    analyzer = StockDataAnalyzer()
    
    # Mock yfinance to return empty data
    mock_ticker = mocker.Mock()
    mock_ticker.history.return_value = pd.DataFrame()
    mocker.patch('yfinance.Ticker', return_value=mock_ticker)
    
    correlation = analyzer.analyze_correlation('INVALID1', 'INVALID2')
    assert correlation == 0.0  # Should return 0 correlation for invalid stocks