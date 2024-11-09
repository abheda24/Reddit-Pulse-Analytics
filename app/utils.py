import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import plotly.graph_objects as go
import base64
from pathlib import Path

def load_css(css_file: Path) -> None:
    """Load and inject custom CSS."""
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_download_link(df: pd.DataFrame, filename: str) -> str:
    """Create a download link for dataframe."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

def format_number(num: float) -> str:
    """Format large numbers for display."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def calculate_growth(current: float, previous: float) -> tuple:
    """Calculate growth percentage and direction."""
    if previous == 0:
        return 0, "neutral"
    growth = ((current - previous) / previous) * 100
    direction = "up" if growth > 0 else "down" if growth < 0 else "neutral"
    return growth, direction

def create_time_filters(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    """Create time-based filters for dataframe."""
    now = datetime.now()
    df['hour'] = pd.to_datetime(df[time_col]).dt.hour
    df['day'] = pd.to_datetime(df[time_col]).dt.day_name()
    df['is_today'] = pd.to_datetime(df[time_col]).dt.date == now.date()
    return df

def create_custom_theme() -> Dict:
    """Create a custom theme for Plotly charts."""
    return {
        'layout': go.Layout(
            font={'family': 'Arial, sans-serif'},
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            title={'font': {'size': 24}},
            xaxis={'gridcolor': '#eee'},
            yaxis={'gridcolor': '#eee'}
        )
    }

def apply_custom_theme_to_figure(fig: go.Figure) -> go.Figure:
    """Apply custom theme to Plotly figure."""
    fig.update_layout(
        font={'family': 'Arial, sans-serif'},
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title={'font': {'size': 24}},
        xaxis={'gridcolor': '#eee'},
        yaxis={'gridcolor': '#eee'}
    )
    return fig