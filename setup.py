from setuptools import setup, find_packages

setup(
    name="reddit_sentiment_analysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'praw',
        'pandas',
        'numpy',
        'plotly',
        'textblob',
        'wordcloud',
        'transformers',
        'torch',
        'yfinance',
        'networkx',
        'python-dotenv',
        'pytest',
        'pytest-mock',
        'pytest-cov',
        'scikit-learn',
        'emoji==0.6.0'  # Added emoji package
    ]
)