"""
News Sentiment Analyzer Application

This application fetches news articles from NewsAPI and uses OpenAI's GPT Assistant
to analyze the sentiment of the news articles. It provides insights into whether
the news coverage around a particular topic is positive, negative, or neutral.

Features:
- Fetches latest news articles from NewsAPI
- Uses OpenAI Assistants API v2 for intelligent sentiment analysis
- Provides sentiment scores and explanations
- Streamlit web interface for easy interaction
- Visualizes sentiment distribution with charts
- Handles function calling for dynamic news retrieval

Use Cases:
- Monitor sentiment around your brand or company
- Analyze public opinion on political topics
- Track sentiment trends for investment decisions
- Research social issues and public perception

Requirements:
- OpenAI API key
- NewsAPI key
- Required packages: openai, streamlit, requests, python-dotenv, plotly

Author: News Sentiment Analyzer Team
Date: 2025
"""

import os
import openai
from dotenv import load_dotenv
import time
import json
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
news_api_key = os.environ.get("NEWS_API_KEY")

# Initialize OpenAI client with v2 Assistants API header
client = openai.OpenAI()
if not hasattr(client, '_default_headers'):
    client._default_headers = {}
client._default_headers["OpenAI-Beta"] = "assistants=v2"

# Default model for OpenAI API
model = "gpt-4"


def get_news_for_sentiment(topic, page_size=10):
    """
    Fetch news articles from NewsAPI for sentiment analysis.
    
    This function queries the NewsAPI to retrieve articles related to the 
    specified topic, optimized for sentiment analysis with more articles
    and focused content selection.
    
    Args:
        topic (str): The topic to search for news articles
        page_size (int): Number of articles to fetch (default: 10)
        
    Returns:
        list: A list of formatted strings containing article information
              optimized for sentiment analysis including:
              - Title
              - Description
              - Source name
              - Publication date
              - Content snippet
              Returns empty list if API request fails.
              
    Example:
        >>> articles = get_news_for_sentiment("climate change")
        >>> print(len(articles))  # Should return up to 10 articles
    """
    # Construct the NewsAPI URL with enhanced parameters for sentiment analysis
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={topic}&"
        f"apiKey={news_api_key}&"
        f"pageSize={page_size}&"
        f"sortBy=publishedAt&"
        f"language=en"
    )

    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            formatted_articles = []

            for i, article in enumerate(articles):
                # Extract article information
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                source_name = article.get("source", {}).get("name", "Unknown source")
                published_at = article.get("publishedAt", "Unknown date")
                content = article.get("content", "No content")
                
                # Create formatted article for sentiment analysis
                article_text = f"""
                Article {i+1}:
                Title: {title}
                Source: {source_name}
                Published: {published_at}
                Description: {description}
                Content: {content[:200]}...
                ---
                """
                formatted_articles.append(article_text)

            return formatted_articles
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API Request: {e}")
        return []


class SentimentAssistantManager:
    """
    Manages interactions with OpenAI's Assistants API v2 for sentiment analysis.
    
    This class specializes in sentiment analysis of news articles, providing
    detailed sentiment scores, explanations, and trend analysis.
    
    Class Attributes:
        thread_id (str): Shared thread ID across instances
        assistant_id (str): Shared assistant ID across instances
        
    Instance Attributes:
        client: OpenAI client instance
        model (str): The GPT model to use
        assistant: The OpenAI assistant object
        thread: The conversation thread object
        run: The current run object
        sentiment_analysis (dict): The generated sentiment analysis results
    """
    
    thread_id = None
    assistant_id = None

    def __init__(self, model: str = model):
        """
        Initialize the SentimentAssistantManager.
        
        Args:
            model (str): The OpenAI model to use (default: gpt-4)
        """
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.sentiment_analysis = None

        # Retrieve existing assistant and thread if IDs are provided
        if SentimentAssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=SentimentAssistantManager.assistant_id
            )
        if SentimentAssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=SentimentAssistantManager.thread_id
            )

    def create_sentiment_assistant(self):
        """
        Create a specialized sentiment analysis assistant.
        
        This assistant is configured with specific instructions for analyzing
        news sentiment and providing detailed, structured analysis.
        """
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name="News Sentiment Analyzer",
                instructions="""You are an expert sentiment analysis assistant specializing in news content. 
                
                Your role is to:
                1. Analyze the sentiment of news articles (positive, negative, neutral)
                2. Provide sentiment scores on a scale of -1 to +1
                3. Explain the reasoning behind your sentiment assessment
                4. Identify key emotional triggers and language patterns
                5. Summarize overall sentiment trends across multiple articles
                
                Always provide structured analysis with:
                - Overall sentiment score (-1 to +1)
                - Sentiment category (Positive/Negative/Neutral)
                - Confidence level (0-100%)
                - Key themes and emotional indicators
                - Brief explanation of your analysis
                
                Be objective and consider context, tone, and implications.""",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_news_for_sentiment",
                            "description": "Fetch news articles for sentiment analysis on a given topic",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "topic": {
                                        "type": "string",
                                        "description": "The topic for news sentiment analysis, e.g. 'Tesla stock', 'climate change'",
                                    },
                                    "page_size": {
                                        "type": "integer",
                                        "description": "Number of articles to analyze (default: 10)",
                                        "default": 10
                                    }
                                },
                                "required": ["topic"],
                            },
                        },
                    }
                ],
                model=self.model,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            SentimentAssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"Sentiment Assistant ID: {self.assistant.id}")

    def create_thread(self):
        """Create a new conversation thread for sentiment analysis."""
        if not self.thread:
            thread_obj = self.client.beta.threads.create(
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            SentimentAssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"Thread ID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        """Add a message to the conversation thread."""
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )

    def run_sentiment_analysis(self, instructions):
        """Start a sentiment analysis run with the assistant."""
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )

    def process_sentiment_results(self):
        """Process and extract sentiment analysis results from the assistant."""
        if self.thread:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            
            last_message = messages.data[0]
            sentiment_response = last_message.content[0].text.value
            
            # Store the sentiment analysis
            self.sentiment_analysis = sentiment_response
            print(f"Sentiment Analysis Complete: {sentiment_response[:200]}...")

    def wait_for_sentiment_completion(self):
        """
        Wait for sentiment analysis completion and handle function calls.
        
        This method manages the entire sentiment analysis workflow including
        function calling for news retrieval and result processing.
        """
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, 
                    run_id=self.run.id,
                    extra_headers={"OpenAI-Beta": "assistants=v2"}
                )
                
                print(f"Run Status: {run_status.status}")
                
                if run_status.status == "completed":
                    self.process_sentiment_results()
                    break
                elif run_status.status == "requires_action":
                    print("Executing sentiment analysis functions...")
                    self.call_sentiment_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    def call_sentiment_functions(self, required_actions):
        """
        Execute functions required for sentiment analysis.
        
        Args:
            required_actions (dict): Function call requirements from the assistant
        """
        if not self.run:
            return
            
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_news_for_sentiment":
                # Get news articles for sentiment analysis
                topic = arguments["topic"]
                page_size = arguments.get("page_size", 10)
                
                articles = get_news_for_sentiment(topic, page_size)
                
                # Combine all articles into a single string for analysis
                combined_articles = "\n".join(articles)
                
                tool_outputs.append({
                    "tool_call_id": action["id"], 
                    "output": combined_articles
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        # Submit function outputs back to the assistant
        print("Submitting news data for sentiment analysis...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, 
            run_id=self.run.id, 
            tool_outputs=tool_outputs,
            extra_headers={"OpenAI-Beta": "assistants=v2"}
        )

    def get_sentiment_analysis(self):
        """Get the sentiment analysis results."""
        return self.sentiment_analysis

    def parse_sentiment_data(self):
        """
        Parse sentiment analysis text to extract structured data for visualization.
        
        Returns:
            dict: Parsed sentiment data including scores and categories
        """
        if not self.sentiment_analysis:
            return None
            
        # Simple parsing logic - in a real application, you might want more sophisticated parsing
        analysis_text = self.sentiment_analysis.lower()
        
        # Extract sentiment score (rough estimation)
        if "positive" in analysis_text:
            if "very positive" in analysis_text or "highly positive" in analysis_text:
                score = 0.8
            elif "moderately positive" in analysis_text:
                score = 0.5
            else:
                score = 0.3
            category = "Positive"
        elif "negative" in analysis_text:
            if "very negative" in analysis_text or "highly negative" in analysis_text:
                score = -0.8
            elif "moderately negative" in analysis_text:
                score = -0.5
            else:
                score = -0.3
            category = "Negative"
        else:
            score = 0.0
            category = "Neutral"
            
        return {
            "score": score,
            "category": category,
            "confidence": 85,  # Default confidence
            "analysis": self.sentiment_analysis
        }


def create_sentiment_visualization(sentiment_data):
    """
    Create visualizations for sentiment analysis results.
    
    Args:
        sentiment_data (dict): Parsed sentiment analysis data
        
    Returns:
        tuple: Plotly figures for sentiment visualization
    """
    if not sentiment_data:
        return None, None
    
    # Sentiment gauge chart
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = sentiment_data["score"],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Sentiment Score"},
        delta = {'reference': 0},
        gauge = {
            'axis': {'range': [None, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.3], 'color': "lightgray"},
                {'range': [-0.3, 0.3], 'color': "gray"},
                {'range': [0.3, 1], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))
    
    gauge_fig.update_layout(
        height=400,
        title="News Sentiment Analysis"
    )
    
    # Sentiment category pie chart
    categories = ["Positive", "Neutral", "Negative"]
    if sentiment_data["category"] == "Positive":
        values = [sentiment_data["confidence"], 100-sentiment_data["confidence"], 0]
        colors = ['#00CC96', '#FFA15A', '#EF553B']
    elif sentiment_data["category"] == "Negative":
        values = [0, 100-sentiment_data["confidence"], sentiment_data["confidence"]]
        colors = ['#00CC96', '#FFA15A', '#EF553B']
    else:
        values = [0, sentiment_data["confidence"], 100-sentiment_data["confidence"]]
        colors = ['#00CC96', '#FFA15A', '#EF553B']
    
    pie_fig = px.pie(
        values=values, 
        names=categories, 
        title="Sentiment Distribution",
        color_discrete_sequence=colors
    )
    
    return gauge_fig, pie_fig


def main():
    """
    Main function that creates and runs the News Sentiment Analyzer application.
    
    This Streamlit app provides an interface for analyzing news sentiment,
    displaying results with visualizations and detailed analysis.
    """
    st.set_page_config(
        page_title="News Sentiment Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    # Header
    st.title("📊 News Sentiment Analyzer")
    st.markdown("""
    Analyze the sentiment of news coverage around any topic using AI-powered sentiment analysis.
    Get insights into public perception, market sentiment, and trending opinions.
    """)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        st.markdown("Configure your sentiment analysis")
        
        # Advanced options
        with st.expander("Advanced Options"):
            article_count = st.slider("Number of articles to analyze", 5, 20, 10)
            include_charts = st.checkbox("Include visualization charts", True)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input form
        with st.form(key="sentiment_input_form"):
            st.subheader("🔍 Enter Topic for Sentiment Analysis")
            topic = st.text_input(
                "Topic:", 
                placeholder="e.g., Tesla stock, climate change, Bitcoin, artificial intelligence"
            )
            
            analysis_type = st.selectbox(
                "Analysis Focus:",
                ["General Sentiment", "Market Sentiment", "Public Opinion", "Brand Perception"]
            )
            
            submit_button = st.form_submit_button(
                label="🚀 Analyze Sentiment", 
                use_container_width=True
            )
    
    with col2:
        st.subheader("📈 Quick Stats")
        st.metric("Articles Analyzed", "0", "Ready to start")
        st.metric("Avg. Processing Time", "~30 sec", "Estimated")
    
    # Process sentiment analysis
    if submit_button:
        if not topic.strip():
            st.error("⚠️ Please enter a topic to analyze.")
            return
        
        # Initialize sentiment analyzer
        manager = SentimentAssistantManager()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Create assistant
            status_text.text("🤖 Creating sentiment analysis assistant...")
            progress_bar.progress(20)
            manager.create_sentiment_assistant()
            
            # Step 2: Create thread
            status_text.text("💬 Setting up analysis session...")
            progress_bar.progress(40)
            manager.create_thread()
            
            # Step 3: Add analysis request
            status_text.text("📝 Preparing analysis request...")
            progress_bar.progress(60)
            analysis_prompt = f"""
            Please analyze the sentiment of news articles about '{topic}' with focus on {analysis_type.lower()}.
            
            Provide:
            1. Overall sentiment score (-1 to +1)
            2. Sentiment category (Positive/Negative/Neutral)
            3. Confidence level (0-100%)
            4. Key themes and emotional indicators
            5. Brief explanation of your analysis
            6. Notable trends or patterns in the coverage
            """
            
            manager.add_message_to_thread("user", analysis_prompt)
            
            # Step 4: Run analysis
            status_text.text("🔍 Running sentiment analysis...")
            progress_bar.progress(80)
            manager.run_sentiment_analysis("Perform comprehensive sentiment analysis")
            
            # Step 5: Wait for completion
            status_text.text("⏳ Processing results...")
            manager.wait_for_sentiment_completion()
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Display results
            sentiment_result = manager.get_sentiment_analysis()
            
            if sentiment_result:
                st.success("🎉 Sentiment analysis completed successfully!")
                
                # Parse sentiment data for visualization
                sentiment_data = manager.parse_sentiment_data()
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Analysis Results", "📈 Visualizations", "🔧 Raw Data"])
                
                with tab1:
                    st.subheader("Sentiment Analysis Results")
                    
                    # Display key metrics
                    if sentiment_data:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Sentiment Score", 
                                f"{sentiment_data['score']:.2f}",
                                delta=f"{sentiment_data['category']}"
                            )
                        with col2:
                            st.metric(
                                "Category", 
                                sentiment_data['category'],
                                delta=f"{sentiment_data['confidence']}% confidence"
                            )
                        with col3:
                            st.metric("Articles Analyzed", article_count)
                    
                    # Display detailed analysis
                    st.subheader("Detailed Analysis")
                    st.write(sentiment_result)
                
                with tab2:
                    if include_charts and sentiment_data:
                        st.subheader("Sentiment Visualizations")
                        
                        gauge_fig, pie_fig = create_sentiment_visualization(sentiment_data)
                        
                        if gauge_fig and pie_fig:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.plotly_chart(gauge_fig, use_container_width=True)
                            with col2:
                                st.plotly_chart(pie_fig, use_container_width=True)
                    else:
                        st.info("Enable 'Include visualization charts' in settings to see charts.")
                
                with tab3:
                    st.subheader("Raw Analysis Data")
                    st.code(sentiment_result, language="text")
                    
                    # Display run steps for debugging
                    with st.expander("Debug Information"):
                        st.text("This section contains technical details about the analysis process.")
                        # You could add run steps here if needed
                        
            else:
                st.error("❌ Could not complete sentiment analysis. Please try again.")
                
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
            print(f"Error in sentiment analysis: {e}")
        
        finally:
            progress_bar.empty()
            status_text.empty()
    
    # Footer
    st.markdown("---")
    st.markdown("**News Sentiment Analyzer** - Powered by OpenAI GPT-4 and NewsAPI")


if __name__ == "__main__":
    main()
