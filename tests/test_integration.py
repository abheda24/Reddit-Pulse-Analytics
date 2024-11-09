import pytest
import pandas as pd
from src.data_collector import RedditDataCollector
from src.sentiment_analyzer import SentimentAnalyzer
from src.data_processor import RedditDataProcessor

def test_end_to_end_flow(mocker, sample_reddit_data, mock_reddit_response):
    """Test complete data flow from collection to processing."""
    # Setup
    collector = RedditDataCollector()
    processor = RedditDataProcessor()
    
    # Mock Reddit data collection
    mock_subreddit = mocker.Mock()
    mock_subreddit.hot.return_value = mock_reddit_response
    mocker.patch.object(
        collector.reddit,
        'subreddit',
        return_value=mock_subreddit
    )
    
    # Process flow
    df = collector.fetch_subreddit_data('wallstreetbets', limit=1)
    processed_df, insights = processor.process_reddit_data(df)
    
    # Assertions
    assert len(processed_df) == len(df)
    assert 'sentiment' in processed_df.columns
    assert 'trending_topics' in insights
    assert insights.get('engagement_stats', {}).get('avg_score', 0) > 0

def test_error_scenarios():
    """Test error handling in the complete flow."""
    processor = RedditDataProcessor()
    
    # Test with invalid DataFrame
    with pytest.raises(ValueError):
        invalid_df = pd.DataFrame({'invalid': [1, 2, 3]})
        processor.process_reddit_data(invalid_df)