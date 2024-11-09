import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from src.data_collector import RedditDataCollector
from src.sentiment_analyzer import SentimentAnalyzer
from src.data_processor import RedditDataProcessor
import time
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

class ModernRedditDashboard:
    def __init__(self):
        self.setup_page_config()
        self.reddit_collector = RedditDataCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_processor = RedditDataProcessor()

    def setup_page_config(self):
        """Configure the page with modern styling."""
        st.set_page_config(
            page_title="Reddit Pulse Analytics",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Apply custom CSS
        st.markdown("""
        <style>
        /* Modern Theme */
        :root {
            --primary-color: #ff4b4b;
            --secondary-color: #1e88e5;
            --background-dark: #0e1117;
            --card-dark: #1e1e2e;
            --text-color: #ffffff;
        }
        
        /* Header Styling */
        .dashboard-header {
            padding: 1rem;
            margin-bottom: 2rem;
            text-align: center;
            background: linear-gradient(90deg, #ff4b4b 0%, #ff8f8f 100%);
            border-radius: 10px;
            color: white;
        }
        
        /* Metric Cards */
        .metric-container {
            background-color: var(--card-dark);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-5px);
        }
        
        /* Charts */
        .chart-container {
            background-color: var(--card-dark);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Custom Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: var(--card-dark);
            padding: 10px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: transparent;
            border: none;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255, 75, 75, 0.1);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--primary-color);
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: var(--card-dark);
        }
        
        /* Inputs */
        .stTextInput input,
        .stSelectbox select,
        .stTextArea textarea {
            background-color: #1e1e2e;
            border-color: #363654;
            color: white;
            border-radius: 8px;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #ff4b4b 0%, #ff8f8f 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
        }
        
        /* Progress Bar */
        .stProgress > div > div > div > div {
            background-color: var(--primary-color);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--card-dark);
            border-radius: 8px;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--background-dark);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Loading Animation */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        </style>
        """, unsafe_allow_html=True)

    def run(self):
        """Main dashboard execution."""
        # Header
        st.markdown("""
            <div class="dashboard-header">
                <h1>📊 Reddit Pulse Analytics</h1>
                <p>Real-time sentiment analysis and trend detection</p>
            </div>
        """, unsafe_allow_html=True)

        # Sidebar
        self.create_sidebar()

        # Main content
        try:
            analysis_type = st.session_state.get('analysis_type', 'General Analysis')
            
            if analysis_type == "General Analysis":
                self.show_general_analysis()
            elif analysis_type == "Topic Tracking":
                self.show_topic_analysis()
            else:
                self.show_comparative_analysis()
                
        except Exception as e:
            self.show_error_message(str(e))

    def create_sidebar(self):
        """Create modern sidebar."""
        with st.sidebar:
            st.image("app/assets/images/logo.png", width=100)
            st.markdown("### Analysis Settings")
            
            # Analysis Type
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["General Analysis", "Topic Tracking", "Comparative Analysis"],
                key='analysis_type'
            )
            
            st.markdown("---")
            
            # Dynamic inputs based on analysis type
            if analysis_type == "General Analysis":
                st.text_input("Enter Subreddit", "wallstreetbets", key='subreddit')
            elif analysis_type == "Topic Tracking":
                st.text_input("Enter Subreddit", "news", key='subreddit')
                st.text_area(
                    "Topics to Track",
                    "bitcoin\nai\ntesla",
                    key='topics'
                )
            else:
                st.text_area(
                    "Subreddits to Compare",
                    "wallstreetbets\nstocks\ninvesting",
                    key='subreddits'
                )
            
            # Common settings
            st.markdown("### Data Settings")
            st.slider("Number of Posts", 10, 500, 100, key='post_limit')
            st.selectbox(
                "Time Filter",
                ["hour", "day", "week", "month", "year", "all"],
                key='time_filter'
            )
            
            # Advanced settings
            with st.expander("⚙️ Advanced Settings"):
                st.checkbox("Include Comments", value=True, key='include_comments')
                st.checkbox("NSFW Content", value=False, key='nsfw')
                st.slider("Minimum Score", 0, 1000, 0, key='min_score')
            
            # Analytics guide
            with st.expander("📈 Analytics Guide"):
                st.markdown("""
                **Metrics Guide:**
                - **Sentiment Score**: -1 (negative) to 1 (positive)
                - **Engagement Rate**: Post interactions vs. average
                - **Trending Score**: Weighted popularity metric
                
                **Tips:**
                - Use longer timeframes for trend analysis
                - Compare multiple subreddits for context
                - Track specific topics for deeper insights
                """)
            
            # Refresh button
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.session_state['last_refresh'] = datetime.now()
                st.experimental_rerun()
            
            # Last update time
            if 'last_refresh' in st.session_state:
                st.markdown(
                    f"*Last updated: {st.session_state['last_refresh'].strftime('%H:%M:%S')}*"
                )
                
    def show_general_analysis(self):
        """Display general subreddit analysis with modern visualizations."""
        try:
            subreddit = st.session_state.get('subreddit', 'wallstreetbets')
            
            # Loading animation
            with st.spinner(f"Analyzing r/{subreddit}..."):
                placeholder = st.empty()
                placeholder.markdown("""
                    <div class="loading-spinner">
                        <div class="pulse">🔄</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Fetch and process data
                df = self.reddit_collector.fetch_subreddit_data(
                    subreddit,
                    st.session_state.get('post_limit', 100)
                )
                processed_df, insights = self.data_processor.process_reddit_data(df)
                placeholder.empty()
                
                # Summary metrics
                self.show_summary_metrics(processed_df, insights)
                
                # Main analysis tabs
                tab_sentiment, tab_trending, tab_engagement, tab_posts = st.tabs([
                    "📊 Sentiment Analysis", 
                    "🔥 Trending Topics", 
                    "📈 Engagement Metrics",
                    "📝 Top Posts"
                ])
                
                with tab_sentiment:
                    self.show_sentiment_analysis(processed_df)
                
                with tab_trending:
                    self.show_trending_topics(insights, processed_df)
                
                with tab_engagement:
                    self.show_engagement_metrics(processed_df)
                
                with tab_posts:
                    self.show_top_posts(processed_df)
                    
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
    
    def show_summary_metrics(self, df, insights):
        """Display modern summary metrics."""
        total_posts = len(df)
        recent_posts = len(df[df['created_utc'] > datetime.now() - timedelta(hours=24)])
        
        cols = st.columns(4)
        metrics = [
            {
                "title": "Total Posts",
                "value": f"{total_posts:,}",
                "delta": f"+{recent_posts} today",
                "icon": "📝"
            },
            {
                "title": "Avg Sentiment",
                "value": f"{df['sentiment_score'].mean():.2f}",
                "delta": "sentiment score",
                "icon": "😊"
            },
            {
                "title": "Engagement Rate",
                "value": f"{df['score'].mean():,.0f}",
                "delta": "per post",
                "icon": "⭐"
            },
            {
                "title": "Total Comments",
                "value": f"{df['num_comments'].sum():,}",
                "delta": f"{df['num_comments'].mean():.1f} per post",
                "icon": "💬"
            }
        ]
        
        for col, metric in zip(cols, metrics):
            with col:
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 24px; margin-bottom: 8px;">
                            {metric['icon']} {metric['title']}
                        </div>
                        <div style="font-size: 32px; font-weight: bold; color: var(--primary-color);">
                            {metric['value']}
                        </div>
                        <div style="font-size: 14px; color: #666;">
                            {metric['delta']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    def show_sentiment_analysis(self, df):
        """Display detailed sentiment analysis."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="chart-container">
                    <h3>Sentiment Distribution</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Sentiment pie chart
            fig = px.pie(
                df,
                names='sentiment',
                values='score',
                color='sentiment',
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                },
                hole=0.4
            )
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title=None
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
                <div class="chart-container">
                    <h3>Sentiment Over Time</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Time series analysis
            df['hour'] = df['created_utc'].dt.hour
            hourly_sentiment = df.groupby(['hour', 'sentiment']).size().unstack()
            
            fig = go.Figure()
            
            for sentiment in hourly_sentiment.columns:
                fig.add_trace(go.Scatter(
                    x=hourly_sentiment.index,
                    y=hourly_sentiment[sentiment],
                    name=sentiment,
                    mode='lines+markers',
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Hour of Day",
                yaxis_title="Number of Posts"
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def show_trending_topics(self, insights, df):
        """Display trending topics analysis."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="chart-container">
                    <h3>Topic Cloud</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Generate word cloud
            text = ' '.join(df['title'] + ' ' + df['text'])
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='#1e1e2e',
                colormap='viridis',
                max_words=100
            ).generate(text)
            
            fig, ax = plt.subplots(figsize=(10,5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_facecolor('#1e1e2e')
            fig.patch.set_facecolor('#1e1e2e')
            
            st.pyplot(fig)
        
        with col2:
            st.markdown("""
                <div class="chart-container">
                    <h3>Top Trending Topics</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if insights['trending_topics']:
                topics_df = pd.DataFrame(insights['trending_topics'])
                fig = px.bar(
                    topics_df.head(10),
                    x='topic',
                    y='count',
                    color='count',
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
    def show_topic_analysis(self):
        """Display topic-specific analysis with modern visualizations."""
        try:
            # Get inputs from session state
            subreddit = st.session_state.get('subreddit', 'all')
            topics = [
                topic.strip() 
                for topic in st.session_state.get('topics', '').split('\n') 
                if topic.strip()
            ]
            post_limit = st.session_state.get('post_limit', 100)
            
            if not topics:
                st.warning("Please enter at least one topic to track")
                return

            # Loading animation
            with st.spinner(f"Analyzing topics in r/{subreddit}..."):
                placeholder = st.empty()
                placeholder.markdown("""
                    <div class="loading-spinner">
                        <div class="pulse">🔄</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Fetch data
                df = self.reddit_collector.fetch_subreddit_data(subreddit, post_limit)
                processed_df, _ = self.data_processor.process_reddit_data(df)
                placeholder.empty()
                
                # Topic analysis
                topic_data = []
                for topic in topics:
                    topic = topic.lower()
                    # Search in both title and text
                    topic_mask = (
                        processed_df['title'].str.lower().str.contains(topic, na=False) |
                        processed_df['text'].str.lower().str.contains(topic, na=False)
                    )
                    topic_posts = processed_df[topic_mask]
                    
                    if not topic_posts.empty:
                        topic_data.append({
                            'topic': topic,
                            'mentions': len(topic_posts),
                            'avg_sentiment_score': topic_posts['sentiment_score'].mean(),
                            'avg_score': topic_posts['score'].mean(),
                            'total_comments': topic_posts['num_comments'].sum(),
                            'positive_ratio': (topic_posts['sentiment'] == 'positive').mean()
                        })
                
                if topic_data:
                    # Create DataFrame for topics
                    topic_df = pd.DataFrame(topic_data)
                    
                    # Summary metrics
                    cols = st.columns(4)
                    
                    with cols[0]:
                        st.markdown("""
                            <div class="metric-container">
                                <h3>📊 Topics Tracked</h3>
                                <div style="font-size: 32px; font-weight: bold; color: var(--primary-color);">
                                    {}</div>
                                <div style="font-size: 14px; color: #666;">
                                    {} with mentions</div>
                            </div>
                        """.format(len(topics), len(topic_data)), unsafe_allow_html=True)
                    
                    with cols[1]:
                        st.markdown("""
                            <div class="metric-container">
                                <h3>🎯 Total Mentions</h3>
                                <div style="font-size: 32px; font-weight: bold; color: var(--primary-color);">
                                    {}</div>
                                <div style="font-size: 14px; color: #666;">
                                    across all topics</div>
                            </div>
                        """.format(topic_df['mentions'].sum()), unsafe_allow_html=True)
                    
                    with cols[2]:
                        most_mentioned = topic_df.loc[topic_df['mentions'].idxmax()]
                        st.markdown("""
                            <div class="metric-container">
                                <h3>🔝 Most Mentioned</h3>
                                <div style="font-size: 32px; font-weight: bold; color: var(--primary-color);">
                                    {}</div>
                                <div style="font-size: 14px; color: #666;">
                                    {} mentions</div>
                            </div>
                        """.format(most_mentioned['topic'], most_mentioned['mentions']), 
                        unsafe_allow_html=True)
                    
                    with cols[3]:
                        most_positive = topic_df.loc[topic_df['positive_ratio'].idxmax()]
                        st.markdown("""
                            <div class="metric-container">
                                <h3>😊 Most Positive</h3>
                                <div style="font-size: 32px; font-weight: bold; color: var(--primary-color);">
                                    {}</div>
                                <div style="font-size: 14px; color: #666;">
                                    {:.1%} positive</div>
                            </div>
                        """.format(most_positive['topic'], most_positive['positive_ratio']), 
                        unsafe_allow_html=True)
                    
                    # Topic Analysis Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                            <div class="chart-container">
                                <h3>Topic Mentions and Engagement</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            name='Mentions',
                            x=topic_df['topic'],
                            y=topic_df['mentions'],
                            marker_color='#ff4b4b'
                        ))
                        
                        fig.add_trace(go.Bar(
                            name='Avg Score',
                            x=topic_df['topic'],
                            y=topic_df['avg_score'],
                            marker_color='#1e88e5',
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            barmode='group',
                            yaxis2=dict(
                                overlaying='y',
                                side='right'
                            ),
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("""
                            <div class="chart-container">
                                <h3>Topic Sentiment Analysis</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        fig = px.scatter(
                            topic_df,
                            x='mentions',
                            y='avg_sentiment_score',
                            size='avg_score',
                            color='positive_ratio',
                            text='topic',
                            color_continuous_scale='RdYlGn',
                            hover_data=['total_comments']
                        )
                        
                        fig.update_traces(
                            textposition='top center',
                            marker=dict(sizeref=2.*max(topic_df['avg_score'])/100**2)
                        )
                        
                        fig.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed Topic Analysis
                    st.markdown("### Detailed Topic Analysis")
                    for topic in topics:
                        topic = topic.lower()
                        topic_posts = processed_df[
                            processed_df['title'].str.lower().str.contains(topic, na=False) |
                            processed_df['text'].str.lower().str.contains(topic, na=False)
                        ]
                        
                        if not topic_posts.empty:
                            with st.expander(f"📊 Analysis for '{topic}'"):
                                st.markdown("""
                                    <div class="metric-container">
                                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                                            <div>
                                                <h4>Total Posts</h4>
                                                <div style="font-size: 24px; color: var(--primary-color);">
                                                    {}</div>
                                            </div>
                                            <div>
                                                <h4>Average Score</h4>
                                                <div style="font-size: 24px; color: var(--primary-color);">
                                                    {:.1f}</div>
                                            </div>
                                            <div>
                                                <h4>Total Comments</h4>
                                                <div style="font-size: 24px; color: var(--primary-color);">
                                                    {}</div>
                                            </div>
                                            <div>
                                                <h4>Avg Sentiment</h4>
                                                <div style="font-size: 24px; color: var(--primary-color);">
                                                    {:.2f}</div>
                                            </div>
                                        </div>
                                    </div>
                                """.format(
                                    len(topic_posts),
                                    topic_posts['score'].mean(),
                                    topic_posts['num_comments'].sum(),
                                    topic_posts['sentiment_score'].mean()
                                ), unsafe_allow_html=True)
                                
                                # Show top posts
                                st.markdown("#### Top Posts")
                                for _, post in topic_posts.nlargest(3, 'score').iterrows():
                                    st.markdown("""
                                        <div class="metric-container" style="margin-top: 10px;">
                                            <h4>{}</h4>
                                            <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                                                <span>Score: {}</span>
                                                <span>Comments: {}</span>
                                                <span>Sentiment: {}</span>
                                            </div>
                                            <div style="color: #666;">{}</div>
                                        </div>
                                    """.format(
                                        post['title'],
                                        post['score'],
                                        post['num_comments'],
                                        post['sentiment'],
                                        post['text'] if post['text'] else 'No content'
                                    ), unsafe_allow_html=True)
                else:
                    st.warning("No mentions found for the specified topics")
                    
        except Exception as e:
            st.error(f"Error in topic analysis: {str(e)}")
            st.info("Please check your inputs and try again")   
            
    def show_comparative_analysis(self):
        """Display comparative analysis of multiple subreddits."""
        try:
            # Get subreddits list
            subreddits = [
                sub.strip() 
                for sub in st.session_state.get('subreddits', '').split('\n') 
                if sub.strip()
            ]
            
            if len(subreddits) < 2:
                st.warning("Please enter at least two subreddits to compare")
                return
                
            post_limit = st.session_state.get('post_limit', 100)
            
            # Loading animation
            with st.spinner("Analyzing subreddits..."):
                placeholder = st.empty()
                placeholder.markdown("""
                    <div class="loading-spinner">
                        <div class="pulse">🔄</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Collect data for each subreddit
                all_data = []
                failed_subreddits = []
                progress_bar = st.progress(0)
                
                for idx, subreddit in enumerate(subreddits):
                    try:
                        df = self.reddit_collector.fetch_subreddit_data(
                            subreddit, 
                            post_limit
                        )
                        processed_df, insights = self.data_processor.process_reddit_data(df)
                        processed_df['subreddit'] = subreddit
                        all_data.append(processed_df)
                    except Exception as e:
                        failed_subreddits.append((subreddit, str(e)))
                    progress_bar.progress((idx + 1) / len(subreddits))
                
                placeholder.empty()
                
                if failed_subreddits:
                    st.warning("Failed to fetch data for some subreddits:")
                    for sub, error in failed_subreddits:
                        st.error(f"r/{sub}: {error}")
                
                if all_data:
                    combined_df = pd.concat(all_data)
                    
                    # Summary metrics
                    st.markdown("""
                        <div class="chart-container">
                            <h2>Subreddit Comparison Summary</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Calculate summary stats
                    summary_data = []
                    for subreddit in subreddits:
                        sub_data = combined_df[combined_df['subreddit'] == subreddit]
                        if not sub_data.empty:
                            summary_data.append({
                                'subreddit': subreddit,
                                'total_posts': len(sub_data),
                                'avg_score': sub_data['score'].mean(),
                                'total_comments': sub_data['num_comments'].sum(),
                                'positive_ratio': (sub_data['sentiment'] == 'positive').mean() * 100,
                                'avg_sentiment': sub_data['sentiment_score'].mean()
                            })
                    
                    # Display summary cards
                    cols = st.columns(len(summary_data))
                    for idx, sub_data in enumerate(summary_data):
                        with cols[idx]:
                            st.markdown(f"""
                                <div class="metric-container">
                                    <h3>r/{sub_data['subreddit']}</h3>
                                    <div style="margin: 15px 0;">
                                        <div style="font-size: 14px; color: #666;">Posts</div>
                                        <div style="font-size: 24px; color: var(--primary-color);">
                                            {sub_data['total_posts']:,}</div>
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <div style="font-size: 14px; color: #666;">Avg Score</div>
                                        <div style="font-size: 24px; color: var(--primary-color);">
                                            {sub_data['avg_score']:,.1f}</div>
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <div style="font-size: 14px; color: #666;">Comments</div>
                                        <div style="font-size: 24px; color: var(--primary-color);">
                                            {sub_data['total_comments']:,}</div>
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <div style="font-size: 14px; color: #666;">Positive Sentiment</div>
                                        <div style="font-size: 24px; color: var(--primary-color);">
                                            {sub_data['positive_ratio']:.1f}%</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Visualization tabs
                    tab_sentiment, tab_engagement, tab_activity, tab_posts = st.tabs([
                        "😊 Sentiment Analysis",
                        "📈 Engagement Metrics",
                        "⏰ Activity Analysis",
                        "📝 Top Posts"
                    ])
                    
                    with tab_sentiment:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                                <div class="chart-container">
                                    <h3>Sentiment Distribution</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            fig = px.histogram(
                                combined_df,
                                x='sentiment',
                                color='subreddit',
                                barmode='group',
                                title=None,
                                template='plotly_dark'
                            )
                            
                            fig.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.markdown("""
                                <div class="chart-container">
                                    <h3>Average Sentiment Score</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            fig = go.Figure()
                            
                            for subreddit in subreddits:
                                sub_data = combined_df[combined_df['subreddit'] == subreddit]
                                fig.add_trace(go.Box(
                                    y=sub_data['sentiment_score'],
                                    name=subreddit,
                                    boxpoints='outliers'
                                ))
                            
                            fig.update_layout(
                                template='plotly_dark',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with tab_engagement:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                                <div class="chart-container">
                                    <h3>Post Score Distribution</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            fig = go.Figure()
                            
                            for subreddit in subreddits:
                                sub_data = combined_df[combined_df['subreddit'] == subreddit]
                                fig.add_trace(go.Box(
                                    y=sub_data['score'],
                                    name=subreddit,
                                    boxpoints='outliers'
                                ))
                            
                            fig.update_layout(
                                template='plotly_dark',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.markdown("""
                                <div class="chart-container">
                                    <h3>Comment Distribution</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            fig = go.Figure()
                            
                            for subreddit in subreddits:
                                sub_data = combined_df[combined_df['subreddit'] == subreddit]
                                fig.add_trace(go.Box(
                                    y=sub_data['num_comments'],
                                    name=subreddit,
                                    boxpoints='outliers'
                                ))
                            
                            fig.update_layout(
                                template='plotly_dark',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with tab_activity:
                        st.markdown("""
                            <div class="chart-container">
                                <h3>Posting Activity by Hour</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        combined_df['hour'] = combined_df['created_utc'].dt.hour
                        activity_df = combined_df.groupby(['subreddit', 'hour']).size().reset_index(name='posts')
                        
                        fig = px.line(
                            activity_df,
                            x='hour',
                            y='posts',
                            color='subreddit',
                            template='plotly_dark'
                        )
                        
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab_posts:
                        st.markdown("### Top Posts by Subreddit")
                        for subreddit in subreddits:
                            with st.expander(f"📊 Top Posts from r/{subreddit}"):
                                sub_posts = combined_df[
                                    combined_df['subreddit'] == subreddit
                                ].nlargest(3, 'score')
                                
                                for _, post in sub_posts.iterrows():
                                    st.markdown(f"""
                                        <div class="metric-container" style="margin-top: 10px;">
                                            <h4>{post['title']}</h4>
                                            <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                                                <span>Score: {post['score']:,}</span>
                                                <span>Comments: {post['num_comments']:,}</span>
                                                <span>Sentiment: {post['sentiment']}</span>
                                            </div>
                                            <div style="color: #666;">{post['text'] if post['text'] else 'No content'}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                else:
                    st.error("Could not fetch data for any of the specified subreddits")
                    
        except Exception as e:
            st.error(f"Error in comparative analysis: {str(e)}")
            st.info("Please check your inputs and try again")                 

    def show_engagement_metrics(self, df):
        """Display engagement analysis."""
        st.markdown("""
            <div class="chart-container">
                <h3>Post Engagement Analysis</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Scatter plot
        fig = px.scatter(
            df,
            x='score',
            y='num_comments',
            color='sentiment',
            size='sentiment_score',
            hover_data=['title'],
            color_discrete_map={
                'positive': '#28a745',
                'negative': '#dc3545',
                'neutral': '#6c757d'
            }
        )
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Engagement timeline
        st.markdown("""
            <div class="chart-container">
                <h3>Engagement Over Time</h3>
            </div>
        """, unsafe_allow_html=True)
        
        df['date'] = df['created_utc'].dt.date
        daily_metrics = df.groupby('date').agg({
            'score': 'mean',
            'num_comments': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['score'],
            name='Average Score',
            line=dict(color='#ff4b4b', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['num_comments'],
            name='Average Comments',
            line=dict(color='#1e88e5', width=3)
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def show_top_posts(self, df):
        """Display top posts analysis."""
        tabs = st.tabs(["🔝 Top Scored", "💬 Most Discussed", "🔥 Trending"])
        
        with tabs[0]:
            self.show_post_cards(df.nlargest(5, 'score'))
        
        with tabs[1]:
            self.show_post_cards(df.nlargest(5, 'num_comments'))
        
        with tabs[2]:
            recent_df = df[
                df['created_utc'] > datetime.now() - timedelta(hours=24)
            ]
            self.show_post_cards(recent_df.nlargest(5, 'score'))

    def show_post_cards(self, posts):
        """Display posts in modern cards."""
        for _, post in posts.iterrows():
            with st.expander(f"📝 {post['title'][:100]}...", expanded=True):
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span style="color: {'#28a745' if post['sentiment']=='positive' else '#dc3545' if post['sentiment']=='negative' else '#6c757d'}">
                                {post['sentiment'].title()} ({post['sentiment_score']:.2f})
                            </span>
                            <span>Score: {post['score']:,}</span>
                            <span>Comments: {post['num_comments']:,}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            {post['text'] if post['text'] else 'No content'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    def show_error_message(self, error):
        """Display error message."""
        st.markdown(f"""
            <div style="background-color: #dc3545; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>😕 Oops! Something went wrong</h3>
                <p>{error}</p>
                <p>Please check your inputs and try again.</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard = ModernRedditDashboard()
    dashboard.run()            