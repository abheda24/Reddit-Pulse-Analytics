import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# API Configurations
REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'user_agent': os.getenv('REDDIT_USER_AGENT')
}

# Model Configurations
MODEL_CONFIG = {
    'sentiment_model': "finiteautomata/bertweet-base-sentiment-analysis",
    'batch_size': 32,
    'cache_dir': './models/cache'
}

# Data Configurations
DATA_CONFIG = {
    'cache_duration': 3600,  # Cache duration in seconds
    'max_posts': 1000,
    'default_timeframe': '24h'
}

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'app.log', 
                maxBytes=1024*1024, 
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )