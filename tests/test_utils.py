# tests/test_utils.py
import pytest
from src.utils import TextPreprocessor, DataProcessor, CacheManager

def test_text_preprocessing():
    """Test text preprocessing functions."""
    text = "Check out $AAPL and @wallstreetbets! http://example.com"
    
    clean_text = TextPreprocessor.clean_text(text)
    assert "http" not in clean_text
    
    mentions = TextPreprocessor.extract_mentions(text)
    assert "wallstreetbets" in mentions
    
    tickers = TextPreprocessor.extract_tickers(text)
    assert "AAPL" in tickers

def test_data_processing(sample_reddit_data):
    """Test data processing functions."""
    processed_df = DataProcessor.calculate_engagement_metrics(sample_reddit_data)
    
    assert 'engagement_score' in processed_df.columns
    assert 'hour_of_day' in processed_df.columns
    assert 'day_of_week' in processed_df.columns

def test_cache_manager():
    """Test cache management."""
    cache = CacheManager(cache_duration=1)  # 1 second cache
    
    # Test cache operations
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'
    
    # Test cache expiration
    import time
    time.sleep(1.1)  # Wait for cache to expire
    assert cache.get('test_key') is None
