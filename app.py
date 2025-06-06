import streamlit as st
from src.ui.dashboard import render_dashboard
from src.ui.analysis import render_analysis
from src.ui.settings import render_settings
from src.ui.reports import render_reports
from src.ui.insider_trading import render_insider_trading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Financial Research Assistant",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("Financial Research Assistant")
    
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        st.sidebar.warning("⚠️ OpenAI API key not set. Some features may be limited.")
        st.sidebar.info("Configure your API keys in the Settings page.")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Analysis", "Insider Trading", "Reports", "Settings"]
    )
    
    # Display the selected page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Analysis":
        render_analysis()
    elif page == "Insider Trading":
        render_insider_trading()
    elif page == "Reports":
        render_reports()
    elif page == "Settings":
        render_settings()

if __name__ == "__main__":
    main() 