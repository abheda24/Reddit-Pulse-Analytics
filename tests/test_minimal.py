import pytest
import pandas as pd
from datetime import datetime
from src.utils import TextPreprocessor

def test_text_processor():
    """Test basic text processing functionality."""
    # Test clean_text
    text = "Hello @user! Check out $AAPL http://example.com"
    cleaned = TextPreprocessor.clean_text(text)
    assert isinstance(cleaned, str)
    assert "http" not in cleaned
    
    # Test extract_mentions
    mentions = TextPreprocessor.extract_mentions(text)
    assert isinstance(mentions, list)
    assert "user" in mentions
    
    # Test extract_tickers
    tickers = TextPreprocessor.extract_tickers(text)
    assert isinstance(tickers, list)
    assert "AAPL" in tickers