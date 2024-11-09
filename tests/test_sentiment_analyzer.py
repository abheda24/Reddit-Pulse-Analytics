# tests/test_sentiment_analyzer.py
import pytest
from src.sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer_initialization():
    """Test sentiment analyzer initialization."""
    analyzer = SentimentAnalyzer()
    assert analyzer is not None
    assert analyzer.sentiment_model is not None

def test_analyze_text():
    """Test single text sentiment analysis."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text("This is a great investment opportunity!")
    
    assert isinstance(result, dict)
    assert 'label' in result
    assert 'score' in result
    assert isinstance(result['score'], float)

def test_analyze_texts_batch():
    """Test batch sentiment analysis."""
    analyzer = SentimentAnalyzer()
    texts = [
        "Great investment!",
        "Terrible losses today",
        "Market is neutral"
    ]
    
    results = analyzer.analyze_texts_batch(texts)
    assert len(results) == len(texts)
    assert all('label' in r for r in results)

def test_empty_text_handling():
    """Test handling of empty text."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text("")
    assert result['label'] == 'neutral'
    assert result['score'] == 0.5

