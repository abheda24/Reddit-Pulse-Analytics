
import pandas as pd
import numpy as np
from typing import Dict, List, Union
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Utility class for text preprocessing."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if pd.isna(text):
            return ""
            
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text)
            
            # Remove special characters
            text = re.sub(r'[^\w\s]', '', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return ""

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract user mentions from text."""
        try:
            mentions = re.findall(r'@(\w+)', text)
            return list(set(mentions))
        except Exception as e:
            logger.error(f"Error extracting mentions: {str(e)}")
            return []

    # src/utils.py (continued)
    @staticmethod
    def extract_tickers(text: str) -> List[str]:
        """Extract stock tickers from text."""
        try:
            # Match patterns like $AAPL or $AMD
            tickers = re.findall(r'\$([A-Za-z]{1,5})', text)
            # Also match common patterns without $ like "AAPL"
            tickers.extend(re.findall(r'\b([A-Z]{2,5})\b', text))
            return list(set(tickers))
        except Exception as e:
            logger.error(f"Error extracting tickers: {str(e)}")
            return []

class DataProcessor:
    """Utility class for data processing and analysis."""
    
    @staticmethod
    def calculate_engagement_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate engagement metrics for posts."""
        try:
            df['engagement_score'] = (
                df['score'] * 1.0 + 
                df['num_comments'] * 2.0
            ) * df['upvote_ratio']
            
            df['hour_of_day'] = df['created_utc'].dt.hour
            df['day_of_week'] = df['created_utc'].dt.day_name()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {str(e)}")
            return df

    @staticmethod
    def identify_trending_topics(
        texts: List[str], 
        min_count: int = 3
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Identify trending topics from a list of texts.
        
        Args:
            texts: List of text content
            min_count: Minimum count to consider a topic trending
            
        Returns:
            List of trending topics with their counts
        """
        try:
            # Combine all texts
            combined_text = ' '.join(texts)
            
            # Remove common words and special characters
            stop_words = set(['the', 'and', 'is', 'in', 'to', 'a', 'for'])
            words = combined_text.lower().split()
            words = [w for w in words if w not in stop_words and len(w) > 2]
            
            # Count occurrences
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1
            
            # Filter trending topics
            trending = [
                {'topic': word, 'count': count}
                for word, count in word_counts.items()
                if count >= min_count
            ]
            
            return sorted(trending, key=lambda x: x['count'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error identifying trending topics: {str(e)}")
            return []

class CacheManager:
    """Utility class for managing data caching."""
    
    def __init__(self, cache_duration: int = 3600):
        self.cache = {}
        self.cache_times = {}
        self.cache_duration = cache_duration

    def get(self, key: str) -> Union[None, any]:
        """Get value from cache if not expired."""
        try:
            if key in self.cache_times:
                if (datetime.now() - self.cache_times[key]).seconds < self.cache_duration:
                    return self.cache.get(key)
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None

    def set(self, key: str, value: any) -> None:
        """Set value in cache with current timestamp."""
        try:
            self.cache[key] = value
            self.cache_times[key] = datetime.now()
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")

class MetricsCalculator:
    """Utility class for calculating various metrics."""
    
    @staticmethod
    def calculate_time_based_metrics(
        df: pd.DataFrame,
        timestamp_col: str = 'created_utc'
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate time-based metrics for the data.
        
        Args:
            df: DataFrame containing timestamp data
            timestamp_col: Name of timestamp column
            
        Returns:
            Dictionary of time-based metrics
        """
        try:
            metrics = {
                'hourly': {},
                'daily': {},
                'weekly': {}
            }
            
            df['hour'] = df[timestamp_col].dt.hour
            df['day'] = df[timestamp_col].dt.day_name()
            df['week'] = df[timestamp_col].dt.isocalendar().week
            
            # Hourly metrics
            hourly_counts = df.groupby('hour').size()
            metrics['hourly'] = {
                'peak_hour': hourly_counts.idxmax(),
                'low_hour': hourly_counts.idxmin(),
                'std_dev': hourly_counts.std()
            }
            
            # Daily metrics
            daily_counts = df.groupby('day').size()
            metrics['daily'] = {
                'peak_day': daily_counts.idxmax(),
                'low_day': daily_counts.idxmin(),
                'std_dev': daily_counts.std()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating time-based metrics: {str(e)}")
            return {'hourly': {}, 'daily': {}, 'weekly': {}}

class DataValidator:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_reddit_data(df: pd.DataFrame) -> bool:
        """
        Validate Reddit data structure.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating if data is valid
        """
        required_columns = [
            'title', 'text', 'score', 'created_utc', 
            'num_comments', 'upvote_ratio'
        ]
        
        try:
            # Check required columns
            if not all(col in df.columns for col in required_columns):
                logger.error("Missing required columns in DataFrame")
                return False
            
            # Check data types
            if not pd.api.types.is_numeric_dtype(df['score']):
                logger.error("Invalid data type for 'score' column")
                return False
                
            if not pd.api.types.is_datetime64_any_dtype(df['created_utc']):
                logger.error("Invalid data type for 'created_utc' column")
                return False
            
            if not pd.api.types.is_numeric_dtype(df['num_comments']):
                logger.error("Invalid data type for 'num_comments' column")
                return False
                
            if not pd.api.types.is_float_dtype(df['upvote_ratio']):
                logger.error("Invalid data type for 'upvote_ratio' column")
                return False
            
            # Check for null values in critical columns
            if df['title'].isnull().any():
                logger.error("Null values found in 'title' column")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False

class ErrorHandler:
    """Utility class for standardized error handling."""
    
    @staticmethod
    def handle_api_error(error: Exception) -> Dict[str, str]:
        """
        Handle API-related errors.
        
        Args:
            error: Exception object
            
        Returns:
            Dictionary with error details
        """
        error_message = str(error)
        error_type = type(error).__name__
        
        logger.error(f"API Error: {error_type} - {error_message}")
        
        return {
            'error_type': error_type,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def handle_data_error(error: Exception) -> Dict[str, str]:
        """
        Handle data processing errors.
        
        Args:
            error: Exception object
            
        Returns:
            Dictionary with error details
        """
        error_message = str(error)
        error_type = type(error).__name__
        
        logger.error(f"Data Error: {error_type} - {error_message}")
        
        return {
            'error_type': error_type,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }