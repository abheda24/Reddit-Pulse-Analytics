import logging
from typing import Dict, List, Union
import pandas as pd
from transformers import pipeline
from textblob import TextBlob  # Fallback option

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """A class for analyzing sentiment in text using transformer models or fallback methods."""
    
    def __init__(self, use_transformers: bool = True):
        """
        Initialize the sentiment analyzer.
        
        Args:
            use_transformers: Whether to use transformer models (requires PyTorch)
        """
        self.use_transformers = use_transformers
        
        try:
            if self.use_transformers:
                self.sentiment_model = pipeline(
                    "sentiment-analysis",
                    model="finiteautomata/bertweet-base-sentiment-analysis"
                )
                logger.info("Initialized transformer-based sentiment analyzer")
            else:
                raise ImportError("Using fallback sentiment analyzer")
                
        except Exception as e:
            logger.warning(f"Failed to load transformer model: {str(e)}")
            logger.info("Using TextBlob for sentiment analysis instead")
            self.use_transformers = False
            self.sentiment_model = None

    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment label and score
        """
        if pd.isna(text) or text.strip() == "":
            return {'label': 'neutral', 'score': 0.5}
            
        try:
            if self.use_transformers:
                result = self.sentiment_model(text)[0]
                return result
            else:
                # Fallback to TextBlob
                analysis = TextBlob(text)
                polarity = analysis.sentiment.polarity
                
                # Convert TextBlob polarity to categorical sentiment
                if polarity > 0.1:
                    label = 'positive'
                    score = min(0.5 + polarity, 1.0)
                elif polarity < -0.1:
                    label = 'negative'
                    score = max(0.5 - abs(polarity), 0.0)
                else:
                    label = 'neutral'
                    score = 0.5
                
                return {'label': label, 'score': score}
                
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {'label': 'neutral', 'score': 0.5}

    def analyze_texts_batch(
        self, 
        texts: List[str]
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Analyze sentiment of multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment dictionaries
        """
        return [self.analyze_text(text) for text in texts]

    def get_sentiment_stats(
        self, 
        df: pd.DataFrame, 
        text_column: str
    ) -> Dict[str, float]:
        """
        Calculate sentiment statistics for a DataFrame.
        
        Args:
            df: DataFrame containing text data
            text_column: Name of the column containing text
            
        Returns:
            Dictionary of sentiment statistics
        """
        try:
            sentiments = self.analyze_texts_batch(df[text_column].tolist())
            
            # Calculate statistics
            sentiment_df = pd.DataFrame(sentiments)
            stats = {
                'positive_ratio': (
                    sentiment_df['label'] == 'positive'
                ).mean(),
                'negative_ratio': (
                    sentiment_df['label'] == 'negative'
                ).mean(),
                'neutral_ratio': (
                    sentiment_df['label'] == 'neutral'
                ).mean(),
                'average_score': sentiment_df['score'].mean(),
                'score_std': sentiment_df['score'].std()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating sentiment stats: {str(e)}")
            return {
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'average_score': 0.5,
                'score_std': 0
            }