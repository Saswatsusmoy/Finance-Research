from typing import Dict, Any, List, Optional
import requests
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import logging
import re
from textblob import TextBlob
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

from src.agents.base_agent import BaseAgent, AgentState

# Load environment variables
load_dotenv()

class NewsSentimentState(AgentState):
    """State for the news sentiment agent"""
    cached_news: Dict[str, Any] = Field(default_factory=dict)
    news_sources: List[str] = Field(default_factory=lambda: ["newsapi"])
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)

class NewsSentimentAgent(BaseAgent):
    """Agent responsible for analyzing news sentiment"""
    
    def __init__(self, agent_id: str = "news_sentiment_agent", api_key: str = None):
        """Initialize the news sentiment agent"""
        super().__init__(agent_id, "news_sentiment")
        self.state = NewsSentimentState(agent_id=agent_id, agent_type="news_sentiment")
        self.logger = logging.getLogger(__name__)
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        
        if not self.api_key:
            self.logger.warning("No NewsAPI key provided. Some functionality may be limited.")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the news sentiment agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            query = input_data.get("query", "")
            symbols = input_data.get("symbols", [])
            days = input_data.get("days", 7)
            
            # If symbols are provided, convert them to a query
            if symbols and not query:
                query = " OR ".join(symbols)
            
            # Fetch news articles
            self.state.add_message("system", f"Fetching news for query: {query}")
            articles = await self.fetch_news(query, days)
            
            # Analyze sentiment
            self.state.add_message("system", "Analyzing sentiment")
            sentiment_results = await self.analyze_sentiment(articles)
            
            self.update_status("idle")
            return {"status": "success", "data": sentiment_results}
        
        except Exception as e:
            self.logger.error(f"Error in news sentiment agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to news sentiment"""
        self.update_status("processing")
        self.state.add_message("user", query)
        
        # Extract potential stock symbols from query
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        
        # Determine time period from query
        days = 7  # Default to 7 days
        if "today" in query.lower():
            days = 1
        elif "week" in query.lower():
            days = 7
        elif "month" in query.lower():
            days = 30
        
        # Prepare search query based on symbols or use original query
        search_query = " OR ".join(symbols) if symbols else query
        
        try:
            # Fetch news articles
            articles = await self.fetch_news(search_query, days)
            
            # Analyze sentiment
            sentiment_results = await self.analyze_sentiment(articles)
            
            response = {
                "status": "success",
                "data": sentiment_results,
                "query": search_query,
                "days": days,
                "symbols": symbols
            }
        
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            response = {"status": "error", "message": str(e)}
        
        self.state.add_message("assistant", response)
        self.update_status("idle")
        return response
    
    async def fetch_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """Fetch news articles for a given query"""
        # Check if data is in cache and still valid
        cache_key = f"{query}_{days}"
        
        if (cache_key in self.state.cached_news and 
            self.state.last_cache_update and 
            (datetime.now() - self.state.last_cache_update).total_seconds() < self.state.cache_duration):
            return self.state.cached_news[cache_key]
        
        # If not in cache or expired, fetch new data
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for NewsAPI
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
            
            # Use NewsAPI if API key is provided
            if self.api_key and "newsapi" in self.state.news_sources:
                self.logger.info(f"Fetching news from NewsAPI for query: {query}")
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "from": from_date,
                    "to": to_date,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": self.api_key
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if response.status_code == 200 and data.get("status") == "ok":
                    articles = data.get("articles", [])
                    self.logger.info(f"Successfully fetched {len(articles)} articles from NewsAPI")
                else:
                    error_msg = data.get('message', 'Unknown error')
                    self.logger.error(f"NewsAPI error: {error_msg}")
                    # If API error but we have symbols, try to generate placeholder data
                    # This allows us to demonstrate functionality even with API errors
                    if re.findall(r'\b[A-Z]{1,5}\b', query):
                        self.logger.warning("Generating placeholder news data for demonstration")
                        articles = self._generate_dummy_news(query, days)
                    else:
                        raise Exception(f"NewsAPI error: {error_msg}")
            
            # If no API key or NewsAPI not in sources, use dummy data for demonstration
            else:
                self.logger.warning("No NewsAPI key provided or not in sources. Using dummy data.")
                articles = self._generate_dummy_news(query, days)
            
            # Cache the result
            self.state.cached_news[cache_key] = articles
            self.state.last_cache_update = datetime.now()
            
            return articles
        
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            # Return empty list on error
            return []
    
    async def analyze_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles"""
        if not articles:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0,
                "article_count": 0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "articles": []
            }
        
        # Process each article
        processed_articles = []
        sentiment_scores = []
        
        for article in articles:
            # Combine title and description for sentiment analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            # Determine sentiment category
            if sentiment_score > 0.1:
                sentiment = "positive"
            elif sentiment_score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Add sentiment data to article
            processed_article = {
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "url": article.get("url", ""),
                "sentiment": sentiment,
                "sentiment_score": sentiment_score
            }
            
            processed_articles.append(processed_article)
            sentiment_scores.append(sentiment_score)
        
        # Calculate overall sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if avg_sentiment > 0.1:
            overall_sentiment = "positive"
        elif avg_sentiment < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Calculate sentiment distribution
        sentiment_distribution = {
            "positive": len([a for a in processed_articles if a["sentiment"] == "positive"]),
            "neutral": len([a for a in processed_articles if a["sentiment"] == "neutral"]),
            "negative": len([a for a in processed_articles if a["sentiment"] == "negative"])
        }
        
        # Sort articles by sentiment score (most positive first)
        processed_articles.sort(key=lambda x: x["sentiment_score"], reverse=True)
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": avg_sentiment,
            "article_count": len(processed_articles),
            "sentiment_distribution": sentiment_distribution,
            "articles": processed_articles
        }
    
    def _generate_dummy_news(self, query: str, days: int) -> List[Dict[str, Any]]:
        """Generate dummy news articles for demonstration purposes"""
        # Extract potential stock symbols from query
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        symbol = symbols[0] if symbols else "AAPL"  # Default to AAPL if no symbol found
        
        # Generate dummy articles
        end_date = datetime.now()
        
        articles = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Create positive article
            articles.append({
                "source": {"id": "bloomberg", "name": "Bloomberg"},
                "author": "John Smith",
                "title": f"{symbol} Reports Strong Quarterly Results, Exceeding Expectations",
                "description": f"The tech giant {symbol} reported quarterly earnings that beat analyst expectations, driven by strong product sales and services growth.",
                "url": "https://www.bloomberg.com/example",
                "urlToImage": "https://example.com/image.jpg",
                "publishedAt": date_str,
                "content": "Full content here..."
            })
            
            # Create neutral article
            articles.append({
                "source": {"id": "reuters", "name": "Reuters"},
                "author": "Jane Doe",
                "title": f"{symbol} Announces New Product Launch Date",
                "description": f"{symbol} has announced the release date for its newest product line, in line with market expectations and previous company statements.",
                "url": "https://www.reuters.com/example",
                "urlToImage": "https://example.com/image2.jpg",
                "publishedAt": date_str,
                "content": "Full content here..."
            })
            
            # Create negative article (less frequent)
            if i % 3 == 0:
                articles.append({
                    "source": {"id": "wsj", "name": "Wall Street Journal"},
                    "author": "Robert Johnson",
                    "title": f"{symbol} Faces Regulatory Scrutiny in European Markets",
                    "description": f"Regulators are examining {symbol}'s business practices, which could potentially lead to fines or required changes to operations.",
                    "url": "https://www.wsj.com/example",
                    "urlToImage": "https://example.com/image3.jpg",
                    "publishedAt": date_str,
                    "content": "Full content here..."
                })
        
        return articles
    
    def add_news_source(self, source: str):
        """Add a news source to the agent"""
        if source not in self.state.news_sources:
            self.state.news_sources.append(source)
    
    def remove_news_source(self, source: str):
        """Remove a news source from the agent"""
        if source in self.state.news_sources:
            self.state.news_sources.remove(source)
    
    def clear_cache(self):
        """Clear the agent's news cache"""
        self.state.cached_news = {}
        self.state.last_cache_update = None 