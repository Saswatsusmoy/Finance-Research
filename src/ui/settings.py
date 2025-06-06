import streamlit as st
import json
import os
from dotenv import load_dotenv, set_key
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.json")

def load_settings():
    """Load settings from file or create default settings"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return create_default_settings()
    else:
        return create_default_settings()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        
        # Also update .env file with API keys for agent access
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        
        for key, value in settings.get("api_keys", {}).items():
            if value:  # Only set non-empty values
                set_key(env_file, key.upper(), value)
        
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

def create_default_settings():
    """Create default settings"""
    return {
        "api_keys": {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "alpha_vantage_key": os.getenv("ALPHA_VANTAGE_KEY", ""),
            "news_api_key": os.getenv("NEWS_API_KEY", ""),
            "finnhub_key": os.getenv("FINNHUB_KEY", "")
        },
        "data_sources": {
            "market_data": ["yahoo_finance", "alpha_vantage"],
            "news_data": ["news_api"],
            "social_media": ["twitter", "reddit"]
        },
        "refresh_settings": {
            "refresh_interval": "15 minutes",
            "cache_duration": "4 hours"
        },
        "agent_settings": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1024,
            "enabled_agents": ["market_data", "news_sentiment", "technical_analysis", "risk_assessment", "report_generation"],
            "agent_memory": 30,
            "confidence_threshold": 0.75
        },
        "ui_preferences": {
            "theme": "System Default",
            "chart_style": "Modern",
            "default_chart_period": "6 Months"
        }
    }

def render_settings():
    st.title("Settings")
    
    # Load current settings
    settings = load_settings()
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs(["API Keys", "Data Sources", "Agent Settings", "UI Preferences"])
    
    with tab1:
        api_keys = render_api_settings(settings.get("api_keys", {}))
        settings["api_keys"] = api_keys
    
    with tab2:
        data_sources, refresh_settings = render_data_source_settings(
            settings.get("data_sources", {}),
            settings.get("refresh_settings", {})
        )
        settings["data_sources"] = data_sources
        settings["refresh_settings"] = refresh_settings
    
    with tab3:
        agent_settings = render_agent_settings(settings.get("agent_settings", {}))
        settings["agent_settings"] = agent_settings
    
    with tab4:
        ui_preferences = render_ui_settings(settings.get("ui_preferences", {}))
        settings["ui_preferences"] = ui_preferences
    
    # Save settings button
    if st.button("Save Settings", type="primary"):
        if save_settings(settings):
            st.success("Settings saved successfully! API keys have been updated.")
        else:
            st.error("Failed to save settings. Check the logs for details.")

def render_api_settings(current_api_keys):
    st.subheader("API Keys")
    
    # API key inputs
    api_keys = {}
    api_keys["openai_api_key"] = st.text_input(
        "OpenAI API Key", 
        type="password", 
        value=current_api_keys.get("openai_api_key", ""), 
        help="Required for LLM functionality"
    )
    
    api_keys["alpha_vantage_key"] = st.text_input(
        "Alpha Vantage API Key", 
        type="password", 
        value=current_api_keys.get("alpha_vantage_key", ""), 
        help="For financial data"
    )
    
    api_keys["finnhub_key"] = st.text_input(
        "Finnhub API Key", 
        type="password", 
        value=current_api_keys.get("finnhub_key", ""), 
        help="For real-time market data"
    )
    
    api_keys["news_api_key"] = st.text_input(
        "News API Key", 
        type="password", 
        value=current_api_keys.get("news_api_key", ""), 
        help="For news sentiment analysis"
    )
    
    st.info("""
    API keys are required to access various data sources and AI capabilities.
    Your API keys are stored locally and are not shared with any third parties.
    """)
    
    return api_keys

def render_data_source_settings(current_data_sources, current_refresh_settings):
    st.subheader("Data Sources")
    
    # Initialize with defaults if not present
    market_data = current_data_sources.get("market_data", ["yahoo_finance"])
    news_data = current_data_sources.get("news_data", ["news_api"])
    social_media = current_data_sources.get("social_media", ["twitter", "reddit"])
    
    # Market data sources
    st.write("**Market Data Sources**")
    col1, col2, col3 = st.columns(3)
    with col1:
        yahoo_finance = st.checkbox("Yahoo Finance", value="yahoo_finance" in market_data)
    with col2:
        alpha_vantage = st.checkbox("Alpha Vantage", value="alpha_vantage" in market_data)
    with col3:
        finnhub = st.checkbox("Finnhub", value="finnhub" in market_data)
    
    # News data sources
    st.write("**News Data Sources**")
    col1, col2, col3 = st.columns(3)
    with col1:
        news_api = st.checkbox("News API", value="news_api" in news_data)
    with col2:
        financial_times = st.checkbox("Financial Times", value="financial_times" in news_data)
    with col3:
        bloomberg = st.checkbox("Bloomberg", value="bloomberg" in news_data)
    
    # Social media data sources
    st.write("**Social Media Data Sources**")
    col1, col2, col3 = st.columns(3)
    with col1:
        twitter = st.checkbox("Twitter", value="twitter" in social_media)
    with col2:
        reddit = st.checkbox("Reddit", value="reddit" in social_media)
    with col3:
        stocktwits = st.checkbox("StockTwits", value="stocktwits" in social_media)
    
    # Compile data sources
    data_sources = {
        "market_data": [],
        "news_data": [],
        "social_media": []
    }
    
    # Add selected sources
    if yahoo_finance:
        data_sources["market_data"].append("yahoo_finance")
    if alpha_vantage:
        data_sources["market_data"].append("alpha_vantage")
    if finnhub:
        data_sources["market_data"].append("finnhub")
    
    if news_api:
        data_sources["news_data"].append("news_api")
    if financial_times:
        data_sources["news_data"].append("financial_times")
    if bloomberg:
        data_sources["news_data"].append("bloomberg")
    
    if twitter:
        data_sources["social_media"].append("twitter")
    if reddit:
        data_sources["social_media"].append("reddit")
    if stocktwits:
        data_sources["social_media"].append("stocktwits")
    
    # Data refresh settings
    st.write("**Data Refresh Settings**")
    
    refresh_intervals = ["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour", "Daily"]
    default_refresh_index = refresh_intervals.index(current_refresh_settings.get("refresh_interval", "15 minutes")) if current_refresh_settings.get("refresh_interval") in refresh_intervals else 2
    
    refresh_interval = st.selectbox(
        "Data Refresh Interval",
        refresh_intervals,
        index=default_refresh_index
    )
    
    cache_durations = ["1 hour", "4 hours", "12 hours", "1 day", "3 days", "7 days"]
    default_cache_index = cache_durations.index(current_refresh_settings.get("cache_duration", "4 hours")) if current_refresh_settings.get("cache_duration") in cache_durations else 1
    
    cache_duration = st.selectbox(
        "Cache Duration",
        cache_durations,
        index=default_cache_index
    )
    
    refresh_settings = {
        "refresh_interval": refresh_interval,
        "cache_duration": cache_duration
    }
    
    return data_sources, refresh_settings

def render_agent_settings(current_agent_settings):
    st.subheader("Agent Settings")
    
    # Default values
    default_model = current_agent_settings.get("model", "gpt-4")
    default_temp = current_agent_settings.get("temperature", 0.7)
    default_tokens = current_agent_settings.get("max_tokens", 1024)
    enabled_agents = current_agent_settings.get("enabled_agents", ["market_data", "news_sentiment", "technical_analysis", "risk_assessment", "report_generation"])
    default_memory = current_agent_settings.get("agent_memory", 30)
    default_threshold = current_agent_settings.get("confidence_threshold", 0.75)
    
    # LLM model settings
    st.write("**LLM Model Settings**")
    
    models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-opus", "claude-3-sonnet", "llama-3-70b"]
    default_model_index = models.index(default_model) if default_model in models else 1
    
    model = st.selectbox(
        "LLM Model",
        models,
        index=default_model_index
    )
    
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=default_temp, step=0.1)
    max_tokens = st.slider("Max Tokens", min_value=256, max_value=4096, value=default_tokens, step=256)
    
    # Agent behavior settings
    st.write("**Agent Behavior**")
    
    col1, col2 = st.columns(2)
    with col1:
        market_data_enabled = st.checkbox("Enable Market Data Agent", value="market_data" in enabled_agents)
        news_sentiment_enabled = st.checkbox("Enable News Sentiment Agent", value="news_sentiment" in enabled_agents)
        technical_analysis_enabled = st.checkbox("Enable Technical Analysis Agent", value="technical_analysis" in enabled_agents)
    with col2:
        risk_assessment_enabled = st.checkbox("Enable Risk Assessment Agent", value="risk_assessment" in enabled_agents)
        report_generation_enabled = st.checkbox("Enable Report Generation Agent", value="report_generation" in enabled_agents)
        agent_collaboration = st.checkbox("Enable Agent Collaboration", value=True)
    
    # Compile enabled agents
    new_enabled_agents = []
    if market_data_enabled:
        new_enabled_agents.append("market_data")
    if news_sentiment_enabled:
        new_enabled_agents.append("news_sentiment")
    if technical_analysis_enabled:
        new_enabled_agents.append("technical_analysis")
    if risk_assessment_enabled:
        new_enabled_agents.append("risk_assessment")
    if report_generation_enabled:
        new_enabled_agents.append("report_generation")
    
    # Advanced agent settings
    st.write("**Advanced Agent Settings**")
    
    agent_memory = st.slider("Agent Memory (days)", min_value=1, max_value=90, value=default_memory, step=1)
    confidence_threshold = st.slider("Confidence Threshold", min_value=0.5, max_value=0.95, value=default_threshold, step=0.05)
    
    st.expander("Expert Settings", expanded=False).write("""
    - **Agent Reasoning Depth**: 3 steps (default)
    - **Tool Usage Limit**: 5 per query (default)
    - **Memory Retention Policy**: FIFO with importance weighting (default)
    - **Collaboration Protocol**: Consensus with expert override (default)
    """)
    
    # Compile agent settings
    agent_settings = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enabled_agents": new_enabled_agents,
        "agent_memory": agent_memory,
        "confidence_threshold": confidence_threshold,
        "collaboration_enabled": agent_collaboration
    }
    
    return agent_settings

def render_ui_settings(current_ui_preferences):
    st.subheader("UI Preferences")
    
    # Default values
    default_theme = current_ui_preferences.get("theme", "System Default")
    default_chart_style = current_ui_preferences.get("chart_style", "Modern")
    default_period = current_ui_preferences.get("default_chart_period", "6 Months")
    display_options = current_ui_preferences.get("display_options", {
        "show_technical_indicators": True,
        "show_news_feed": True,
        "show_risk_metrics": True,
        "show_performance_metrics": True,
        "show_agent_log": True,
        "show_tooltips": True
    })
    
    # Theme settings
    st.write("**Theme**")
    
    themes = ["Light", "Dark", "System Default"]
    default_theme_index = themes.index(default_theme) if default_theme in themes else 2
    
    theme = st.selectbox(
        "Color Theme",
        themes,
        index=default_theme_index
    )
    
    # Chart settings
    st.write("**Chart Settings**")
    
    chart_styles = ["Modern", "Classic", "Minimal", "Financial"]
    default_style_index = chart_styles.index(default_chart_style) if default_chart_style in chart_styles else 0
    
    chart_style = st.selectbox(
        "Chart Style",
        chart_styles,
        index=default_style_index
    )
    
    periods = ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years", "Max"]
    default_period_index = periods.index(default_period) if default_period in periods else 4
    
    default_chart_period = st.selectbox(
        "Default Chart Period",
        periods,
        index=default_period_index
    )
    
    # Display settings
    st.write("**Display Settings**")
    col1, col2 = st.columns(2)
    with col1:
        show_tech_indicators = st.checkbox("Show Technical Indicators", value=display_options.get("show_technical_indicators", True))
        show_news_feed = st.checkbox("Show News Feed", value=display_options.get("show_news_feed", True))
        show_agent_log = st.checkbox("Show Agent Activity Log", value=display_options.get("show_agent_log", True))
    with col2:
        show_risk_metrics = st.checkbox("Show Risk Metrics", value=display_options.get("show_risk_metrics", True))
        show_perf_metrics = st.checkbox("Show Performance Metrics", value=display_options.get("show_performance_metrics", True))
        show_tooltips = st.checkbox("Show Tooltips", value=display_options.get("show_tooltips", True))
    
    # Compile display options
    display_options = {
        "show_technical_indicators": show_tech_indicators,
        "show_news_feed": show_news_feed,
        "show_risk_metrics": show_risk_metrics,
        "show_performance_metrics": show_perf_metrics,
        "show_agent_log": show_agent_log,
        "show_tooltips": show_tooltips
    }
    
    # Compile UI preferences
    ui_preferences = {
        "theme": theme,
        "chart_style": chart_style,
        "default_chart_period": default_chart_period,
        "display_options": display_options
    }
    
    return ui_preferences

def get_settings():
    """Get the current settings, for use by other components"""
    return load_settings()

def get_api_key(key_name):
    """Get a specific API key"""
    settings = load_settings()
    return settings.get("api_keys", {}).get(key_name, "") 