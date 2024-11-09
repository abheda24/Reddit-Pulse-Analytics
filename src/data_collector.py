import praw
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from functools import lru_cache
import time
from prawcore.exceptions import PrawcoreException
from .config import REDDIT_CONFIG, DATA_CONFIG

logger = logging.getLogger(__name__)

class RedditDataCollector:
    """
    A class to collect and process Reddit data.
    
    Attributes:
        reddit: PRAW Reddit instance
        cache_duration: How long to cache results
    """
    
    def __init__(self, cache_duration: int = DATA_CONFIG['cache_duration']):
        """
        Initialize the Reddit data collector.
        
        Args:
            cache_duration: Cache duration in seconds
        """
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CONFIG['client_id'],
                client_secret=REDDIT_CONFIG['client_secret'],
                user_agent=REDDIT_CONFIG['user_agent']
            )
            self.cache_duration = cache_duration
            logger.info("Reddit client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {str(e)}")
            raise

    @lru_cache(maxsize=32)
    def fetch_subreddit_data(
        self, 
        subreddit_name: str, 
        limit: int = 100, 
        timeframe: str = 'day'
    ) -> pd.DataFrame:
        """
        Fetch posts from specified subreddit with caching.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Maximum number of posts to fetch
            timeframe: Time frame for posts ('hour', 'day', 'week', 'month', 'year')
            
        Returns:
            DataFrame containing post data
        """
        try:
            logger.info(f"Fetching data from r/{subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            
            # Use different sorting based on timeframe
            if timeframe == 'hour':
                posts = subreddit.top('hour', limit=limit)
            else:
                posts = subreddit.hot(limit=limit)
            
            for post in posts:
                try:
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'num_comments': post.num_comments,
                        'upvote_ratio': post.upvote_ratio,
                        'author': str(post.author),
                        'url': post.url,
                        'is_self': post.is_self
                    }
                    posts_data.append(post_data)
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {str(e)}")
                    continue
            
            df = pd.DataFrame(posts_data)
            logger.info(f"Successfully fetched {len(df)} posts from r/{subreddit_name}")
            return df
            
        except PrawcoreException as e:
            logger.error(f"Reddit API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching subreddit data: {str(e)}")
            raise

    def get_post_comments(
        self, 
        post_id: str, 
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch comments for a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            comments = []
            for comment in submission.comments[:limit]:
                try:
                    comment_data = {
                        'id': comment.id,
                        'text': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'author': str(comment.author),
                        'is_submitter': comment.is_submitter
                    }
                    comments.append(comment_data)
                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {str(e)}")
                    continue
                    
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
            return []