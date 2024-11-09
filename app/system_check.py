import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly
import praw
from transformers import pipeline
import yfinance as yf

def check_dependencies():
    """Check if all required packages are working."""
    results = {}
    
    print("Checking system dependencies...")
    
    # Check Streamlit
    try:
        st.title("Test")
        results["Streamlit"] = "✓"
    except Exception as e:
        results["Streamlit"] = f"✗ ({str(e)})"
    
    # Check Pandas
    try:
        pd.DataFrame({'test': [1, 2, 3]})
        results["Pandas"] = "✓"
    except Exception as e:
        results["Pandas"] = f"✗ ({str(e)})"
    
    # Check Plotly
    try:
        import plotly.express as px
        results["Plotly"] = "✓"
    except Exception as e:
        results["Plotly"] = f"✗ ({str(e)})"
    
    # Check PRAW
    try:
        reddit = praw.Reddit(
            client_id="test",
            client_secret="test",
            user_agent="test"
        )
        results["PRAW"] = "✓"
    except Exception as e:
        results["PRAW"] = f"✗ ({str(e)})"
    
    # Check Transformers
    try:
        sentiment = pipeline("sentiment-analysis")
        results["Transformers"] = "✓"
    except Exception as e:
        results["Transformers"] = f"✗ ({str(e)})"
    
    # Check yfinance
    try:
        yf.download("AAPL", period="1d")
        results["yfinance"] = "✓"
    except Exception as e:
        results["yfinance"] = f"✗ ({str(e)})"
    
    return results

def check_reddit_api():
    """Test Reddit API connectivity."""
    try:
        from src.data_collector import RedditDataCollector
        collector = RedditDataCollector()
        df = collector.fetch_subreddit_data("test", limit=1)
        return "✓ Connected"
    except Exception as e:
        return f"✗ Error: {str(e)}"

def run_system_check():
    """Run complete system check."""
    print("Starting System Check...")
    print("=" * 50)
    
    # Check dependencies
    print("\nChecking Dependencies:")
    results = check_dependencies()
    for package, status in results.items():
        print(f"{package}: {status}")
    
    # Check Reddit API
    print("\nChecking Reddit API:")
    api_status = check_reddit_api()
    print(f"API Status: {api_status}")
    
    # Check file structure
    print("\nChecking File Structure:")
    import os
    required_files = [
        "app/dashboard.py",
        "src/data_collector.py",
        "src/sentiment_analyzer.py",
        "src/data_processor.py",
        "src/utils.py",
        ".env"
    ]
    
    for file in required_files:
        status = "✓" if os.path.exists(file) else "✗"
        print(f"{file}: {status}")
    
    print("\nSystem Check Complete!")

if __name__ == "__main__":
    run_system_check()