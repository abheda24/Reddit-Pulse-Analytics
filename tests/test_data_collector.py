# tests/test_data_collector.py
import pytest
from src.data_collector import RedditDataCollector
from prawcore.exceptions import PrawcoreException

def test_reddit_data_collector_initialization():
    """Test Reddit data collector initialization."""
    collector = RedditDataCollector()
    assert collector is not None
    assert collector.reddit is not None

def test_fetch_subreddit_data(mocker, mock_reddit_response):
    """Test fetching subreddit data."""
    collector = RedditDataCollector()
    
    # Mock the subreddit method
    mock_subreddit = mocker.Mock()
    mock_subreddit.hot.return_value = mock_reddit_response
    mocker.patch.object(
        collector.reddit,
        'subreddit',
        return_value=mock_subreddit
    )
    
    df = collector.fetch_subreddit_data('test', limit=1)
    assert len(df) == 1
    assert 'title' in df.columns
    assert 'score' in df.columns

def test_error_handling(mocker):
    """Test error handling in data collection."""
    collector = RedditDataCollector()
    
    # Mock the subreddit method to raise the exception
    mocker.patch.object(
        collector.reddit,
        'subreddit',
        side_effect=PrawcoreException()
    )
    
    with pytest.raises(PrawcoreException):
        collector.fetch_subreddit_data('test')

