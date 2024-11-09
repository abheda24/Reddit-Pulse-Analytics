import pytest
import streamlit as st
from app.dashboard import ModernRedditDashboard
import pandas as pd
from datetime import datetime, timedelta

class TestDashboardFunctionality:
    """Test all dashboard components systematically."""
    
    @pytest.fixture
    def dashboard(self):
        return ModernRedditDashboard()

    def test_general_analysis(self, dashboard: ModernRedditDashboard):
        """Test general analysis functionality."""
        print("\nTesting General Analysis...")
        try:
            # Test with a known subreddit
            st.session_state['subreddit'] = 'wallstreetbets'
            st.session_state['post_limit'] = 10
            
            df = dashboard.reddit_collector.fetch_subreddit_data(
                st.session_state['subreddit'],
                st.session_state['post_limit']
            )
            assert isinstance(df, pd.DataFrame), "Failed to fetch subreddit data"
            assert not df.empty, "Fetched DataFrame is empty"
            
            # Check required columns
            required_columns = ['title', 'score', 'created_utc', 'num_comments']
            assert all(col in df.columns for col in required_columns), \
                "Missing required columns in DataFrame"
            
            print("✓ General Analysis working correctly")
            return True
        except Exception as e:
            print(f"✗ General Analysis Error: {str(e)}")
            return False

    def test_topic_analysis(self, dashboard: ModernRedditDashboard):
        """Test topic tracking functionality."""
        print("\nTesting Topic Analysis...")
        try:
            # Test with sample topics
            st.session_state['subreddit'] = 'news'
            st.session_state['topics'] = 'bitcoin\nai\ntesla'
            st.session_state['post_limit'] = 10
            
            topics = [topic.strip() for topic in st.session_state['topics'].split('\n')]
            df = dashboard.reddit_collector.fetch_subreddit_data(
                st.session_state['subreddit'],
                st.session_state['post_limit']
            )
            
            assert isinstance(df, pd.DataFrame), "Failed to fetch subreddit data"
            assert not df.empty, "Fetched DataFrame is empty"
            
            # Process data
            processed_df, insights = dashboard.data_processor.process_reddit_data(df)
            assert 'sentiment' in processed_df.columns, "Sentiment analysis failed"
            
            print("✓ Topic Analysis working correctly")
            return True
        except Exception as e:
            print(f"✗ Topic Analysis Error: {str(e)}")
            return False

    def test_comparative_analysis(self, dashboard: ModernRedditDashboard):
        """Test comparative analysis functionality."""
        print("\nTesting Comparative Analysis...")
        try:
            # Test with multiple subreddits
            st.session_state['subreddits'] = 'wallstreetbets\nstocks\ninvesting'
            st.session_state['post_limit'] = 10
            
            subreddits = [s.strip() for s in st.session_state['subreddits'].split('\n')]
            all_data = []
            
            for subreddit in subreddits:
                df = dashboard.reddit_collector.fetch_subreddit_data(
                    subreddit,
                    st.session_state['post_limit']
                )
                assert isinstance(df, pd.DataFrame), f"Failed to fetch data for {subreddit}"
                all_data.append(df)
            
            assert len(all_data) > 0, "No data fetched for any subreddit"
            print("✓ Comparative Analysis working correctly")
            return True
        except Exception as e:
            print(f"✗ Comparative Analysis Error: {str(e)}")
            return False

    def test_data_processing(self, dashboard: ModernRedditDashboard):
        """Test data processing functionality."""
        print("\nTesting Data Processing...")
        try:
            df = dashboard.reddit_collector.fetch_subreddit_data('wallstreetbets', 5)
            processed_df, insights = dashboard.data_processor.process_reddit_data(df)
            
            # Check processed data
            assert 'sentiment' in processed_df.columns, "Sentiment analysis failed"
            assert 'sentiment_score' in processed_df.columns, "Sentiment scoring failed"
            assert isinstance(insights, dict), "Insights generation failed"
            
            print("✓ Data Processing working correctly")
            return True
        except Exception as e:
            print(f"✗ Data Processing Error: {str(e)}")
            return False

    def test_visualization_data(self, dashboard: ModernRedditDashboard):
        """Test data preparation for visualizations."""
        print("\nTesting Visualization Data...")
        try:
            df = dashboard.reddit_collector.fetch_subreddit_data('wallstreetbets', 5)
            processed_df, insights = dashboard.data_processor.process_reddit_data(df)
            
            # Check sentiment distribution
            sentiment_counts = processed_df['sentiment'].value_counts()
            assert not sentiment_counts.empty, "Sentiment distribution is empty"
            
            # Check trending topics
            assert 'trending_topics' in insights, "No trending topics generated"
            
            print("✓ Visualization Data working correctly")
            return True
        except Exception as e:
            print(f"✗ Visualization Data Error: {str(e)}")
            return False

def run_all_tests():
    """Run all dashboard tests and generate report."""
    print("Starting Dashboard Functionality Tests...")
    print("=" * 50)
    
    dashboard = ModernRedditDashboard()
    tester = TestDashboardFunctionality()
    
    results = {
        "General Analysis": tester.test_general_analysis(dashboard),
        "Topic Analysis": tester.test_topic_analysis(dashboard),
        "Comparative Analysis": tester.test_comparative_analysis(dashboard),
        "Data Processing": tester.test_data_processing(dashboard),
        "Visualization Data": tester.test_visualization_data(dashboard)
    }
    
    print("\nTest Results Summary:")
    print("=" * 50)
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print("\nOverall Statistics:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    run_all_tests()