# src/data_processor.py
from typing import Dict, List, Tuple, Union, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from .utils import TextPreprocessor, DataProcessor, MetricsCalculator, DataValidator
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

class RedditDataProcessor:
    """
    Class for processing and analyzing Reddit data.
    
    This class combines various utilities to process Reddit data
    and extract meaningful insights.
    """
    
    def __init__(self, sentiment_analyzer: Optional[SentimentAnalyzer] = None):
        """
        Initialize the data processor.
        
        Args:
            sentiment_analyzer: Optional sentiment analyzer instance
        """
        self.text_processor = TextPreprocessor()
        self.metrics_calculator = MetricsCalculator()
        self.data_validator = DataValidator()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()

    def process_reddit_data(
        self, 
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Process Reddit data and extract insights.
        
        Args:
            df: Raw Reddit data DataFrame
            
        Returns:
            Tuple of processed DataFrame and insights dictionary
        """
        try:
            # Validate data
            if not self.data_validator.validate_reddit_data(df):
                raise ValueError("Invalid Reddit data format")

            # Clean text
            df['clean_title'] = df['title'].apply(self.text_processor.clean_text)
            df['clean_text'] = df['text'].apply(self.text_processor.clean_text)

            # Extract features
            df['mentions'] = df['clean_text'].apply(self.text_processor.extract_mentions)
            df['tickers'] = df['clean_text'].apply(self.text_processor.extract_tickers)

            # Calculate engagement metrics
            df = DataProcessor.calculate_engagement_metrics(df)

            # Analyze sentiment
            sentiment_results = self.sentiment_analyzer.analyze_texts_batch(
                df['clean_title'] + " " + df['clean_text']
            )
            df['sentiment'] = [r['label'] for r in sentiment_results]
            df['sentiment_score'] = [r['score'] for r in sentiment_results]

            # Calculate insights
            insights = self._calculate_insights(df)

            return df, insights

        except Exception as e:
            logger.error(f"Error processing Reddit data: {str(e)}")
            raise

    def _calculate_insights(self, df: pd.DataFrame) -> Dict:
        """
        Calculate various insights from processed data.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary of insights
        """
        insights = {}
        
        try:
            # Time-based metrics
            insights['time_metrics'] = self.metrics_calculator.calculate_time_based_metrics(
                df, 'created_utc'
            )

            # Trending topics
            insights['trending_topics'] = DataProcessor.identify_trending_topics(
                df['clean_title'].tolist() + df['clean_text'].tolist()
            )

            # Sentiment distribution
            sentiment_counts = df['sentiment'].value_counts()
            insights['sentiment_distribution'] = sentiment_counts.to_dict()

            # Top tickers
            all_tickers = [ticker for tickers in df['tickers'] for ticker in tickers]
            ticker_counts = pd.Series(all_tickers).value_counts()
            insights['top_tickers'] = ticker_counts.head(10).to_dict()

            # Engagement stats
            insights['engagement_stats'] = {
                'avg_score': df['score'].mean(),
                'avg_comments': df['num_comments'].mean(),
                'top_posts': df.nlargest(5, 'engagement_score')[
                    ['title', 'engagement_score']
                ].to_dict('records')
            }

            return insights

        except Exception as e:
            logger.error(f"Error calculating insights: {str(e)}")
            return {}

    def generate_report(
        self, 
        df: pd.DataFrame, 
        insights: Dict
    ) -> Dict[str, Union[str, Dict]]:
        """
        Generate a comprehensive report from processed data.
        
        Args:
            df: Processed DataFrame
            insights: Dictionary of insights
            
        Returns:
            Report dictionary
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'total_posts': len(df),
                    'date_range': {
                        'start': df['created_utc'].min().isoformat(),
                        'end': df['created_utc'].max().isoformat()
                    },
                    'unique_authors': df['author'].nunique()
                },
                'sentiment_analysis': {
                    'overall_sentiment': df['sentiment'].mode()[0],
                    'sentiment_distribution': insights['sentiment_distribution'],
                    'average_sentiment_score': df['sentiment_score'].mean()
                },
                'trending_topics': insights['trending_topics'][:10],
                'engagement_metrics': insights['engagement_stats'],
                'time_analysis': insights['time_metrics']
            }

            if 'top_tickers' in insights:
                report['stock_analysis'] = {
                    'top_tickers': insights['top_tickers'],
                    'ticker_sentiment': self._calculate_ticker_sentiment(df)
                }

            return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {'error': str(e)}

    def _calculate_ticker_sentiment(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Calculate sentiment metrics for each ticker.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary of ticker sentiment metrics
        """
        ticker_sentiment = {}
        
        try:
            for idx, row in df.iterrows():
                for ticker in row['tickers']:
                    if ticker not in ticker_sentiment:
                        ticker_sentiment[ticker] = {
                            'positive': 0,
                            'negative': 0,
                            'neutral': 0,
                            'total_mentions': 0
                        }
                    
                    ticker_sentiment[ticker][row['sentiment']] += 1
                    ticker_sentiment[ticker]['total_mentions'] += 1

            # Calculate percentages
            for ticker in ticker_sentiment:
                total = ticker_sentiment[ticker]['total_mentions']
                for sentiment in ['positive', 'negative', 'neutral']:
                    ticker_sentiment[ticker][f'{sentiment}_ratio'] = (
                        ticker_sentiment[ticker][sentiment] / total
                    )

            return ticker_sentiment

        except Exception as e:
            logger.error(f"Error calculating ticker sentiment: {str(e)}")
            return {}