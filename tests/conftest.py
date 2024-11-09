import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_reddit_data():
    """Fixture providing sample Reddit data for testing."""
    return pd.DataFrame({
        'title': [
            'AAPL earnings discussion', 
            'GME to the moon', 
            'Technical analysis of TSLA'
        ],
        'text': [
            'Apple earnings beat expectations $AAPL',
            'GME showing strong momentum @wallstreetbets',
            'TSLA price target increased by analysts'
        ],
        'score': np.array([100, 150, 75], dtype=np.int64),  # Explicitly set dtype
        'created_utc': pd.to_datetime([
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=1),
            datetime.now()
        ]),
        'num_comments': np.array([50, 75, 25], dtype=np.int64),
        'upvote_ratio': np.array([0.95, 0.88, 0.92], dtype=np.float64),
        'author': ['user1', 'user2', 'user3'],
        'id': ['abc123', 'def456', 'ghi789']
    })

@pytest.fixture
def mock_reddit_response(mocker):
    """Fixture providing mocked Reddit API response."""
    mock_submission = mocker.Mock()
    mock_submission.id = 'abc123'
    mock_submission.title = 'Test Post'
    mock_submission.selftext = 'Test Content'
    mock_submission.score = 100
    mock_submission.created_utc = datetime.now().timestamp()
    mock_submission.num_comments = 10
    mock_submission.upvote_ratio = 0.9
    mock_submission.author = mocker.Mock(name='testuser')
    return [mock_submission]