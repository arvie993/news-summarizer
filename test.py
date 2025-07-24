"""
News Summarizer Test/Development Version

This is a test version of the news summarizer application that serves as
an alternative implementation and testing ground for the main application.
It contains similar functionality but may have different configurations
or experimental features.

Key Differences from main.py:
- Uses gpt-3.5-turbo-16k model for larger context
- Slightly different assistant instructions
- May contain experimental features or bug fixes
- Used for testing before implementing in main.py

Features:
- Fetches latest news articles from NewsAPI
- Uses OpenAI Assistants API for intelligent summarization
- Streamlit web interface for easy interaction
- Handles function calling for dynamic news retrieval

Requirements:
- OpenAI API key
- NewsAPI key
- Required packages: openai, streamlit, requests, python-dotenv

Author: News Summarizer Team
Date: 2025
"""

import openai
import os
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import requests
import json
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
news_api_key = os.environ.get("NEWS_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI()

# Using a larger context model for testing
model = "gpt-3.5-turbo-16k"


def get_news(topic):
    """
    Fetch news articles from NewsAPI based on a given topic.
    
    This function queries the NewsAPI to retrieve the latest 5 articles
    related to the specified topic and formats them for processing.
    This is the test version that may include additional error handling
    or different formatting approaches.
    
    Args:
        topic (str): The topic to search for news articles (e.g., "bitcoin", "AI")
        
    Returns:
        list: A list of formatted strings containing article information including:
              - Title
              - Author
              - Source name
              - Description
              - URL
              Returns empty list if API request fails.
              
    Raises:
        requests.exceptions.RequestException: If there's an error with the API request
        
    Example:
        >>> articles = get_news("bitcoin")
        >>> print(len(articles))  # Should return up to 5 articles
    """
    # Construct the NewsAPI URL with the topic and API key
    url = (
        f"https://newsapi.org/v2/everything?q={topic}&apiKey={news_api_key}&pageSize=5"
    )

    try:
        # Make the API request
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the JSON response
            news = json.dumps(response.json(), indent=4)
            news_json = json.loads(news)
            data = news_json

            # Extract metadata from the response
            status = data["status"]
            total_results = data["totalResults"]
            articles = data["articles"]
            final_news = []

            # Process each article and format the information
            for article in articles:
                source_name = article["source"]["name"]
                author = article["author"]
                title = article["title"]
                description = article["description"]
                url = article["url"]
                content = article["content"]
                
                # Create a formatted string with article details
                title_description = f"""
                   Title: {title}, 
                   Author: {author},
                   Source: {source_name},
                   Description: {description},
                   URL: {url}
            
                """
                final_news.append(title_description)

            return final_news
        else:
            # Return empty list if API request was not successful
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API Request: {e}")
        return []


class AssistantManager:
    """
    Test version of the AssistantManager class for OpenAI's Assistants API.
    
    This class manages interactions with OpenAI's Assistants API and serves
    as a testing ground for new features and improvements before implementing
    them in the main application.
    
    Key differences from main.py version:
    - Uses standard API headers (no v2 beta headers)
    - Different method names for some functions (run_assistant vs run_assitant)
    - May include experimental error handling or features
    
    Class Attributes:
        thread_id (str): Shared thread ID across instances
        assistant_id (str): Shared assistant ID across instances
        
    Instance Attributes:
        client: OpenAI client instance
        model (str): The GPT model to use
        assistant: The OpenAI assistant object
        thread: The conversation thread object
        run: The current run object
        summary (str): The generated summary from the assistant
    """
    
    # Class variables to maintain state across instances
    thread_id = None
    assistant_id = None

    def __init__(self, model: str = model):
        """
        Initialize the AssistantManager.
        
        Args:
            model (str): The OpenAI model to use (default: gpt-3.5-turbo-16k)
        """
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        """
        Create a new OpenAI assistant with specified capabilities.
        
        Args:
            name (str): Name for the assistant
            instructions (str): Instructions that define the assistant's behavior
            tools (list): List of tools/functions the assistant can use
            
        Note:
            This test version uses standard API headers without v2 beta features.
            Only creates a new assistant if one doesn't already exist.
        """
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssisID:::: {self.assistant.id}")

    def create_thread(self):
        """
        Create a new conversation thread for the assistant.
        
        A thread represents a conversation session and maintains
        the context of the conversation between user and assistant.
        This test version uses standard API calls.
        """
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        """
        Add a message to the conversation thread.
        
        Args:
            role (str): The role of the message sender ("user" or "assistant")
            content (str): The content of the message
            
        Note:
            This test version uses standard message creation without v2 headers.
        """
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )

    def run_assistant(self, instructions):
        """
        Start a run with the assistant to process the conversation.
        
        Args:
            instructions (str): Specific instructions for this run
            
        Note:
            This method is named 'run_assistant' (vs 'run_assitant' in main.py)
            and uses standard API calls without v2 headers.
        """
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        """
        Process and extract the latest message from the assistant.
        
        Retrieves the most recent message from the conversation thread
        and stores it as a summary. This test version uses standard API calls.
        """
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            # Get the latest message (first in the list)
            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")

    def call_required_functions(self, required_actions):
        """
        Execute functions required by the assistant and submit results.
        
        Args:
            required_actions (dict): Dictionary containing function call details
                                   including function names and arguments
                                   
        Currently supports:
        - get_news: Fetches news articles for a given topic
        
        This test version uses standard API calls for submitting tool outputs.
        
        Raises:
            ValueError: If an unknown function is requested
        """
        if not self.run:
            return
            
        tool_outputs = []

        # Process each required function call
        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_news":
                # Call the get_news function with the provided topic
                output = get_news(topic=arguments["topic"])
                print(f"STUFFFFF;;;;{output}")
                
                # Concatenate all article information into a single string
                final_str = ""
                for item in output:
                    final_str += "".join(item)

                tool_outputs.append({"tool_call_id": action["id"], "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        # Submit the function outputs back to the assistant
        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, 
            run_id=self.run.id, 
            tool_outputs=tool_outputs
        )

    def get_summary(self):
        """
        Get the generated summary from the assistant.
        
        Returns:
            str: The summary text generated by the assistant,
                 or None if no summary is available
        """
        return self.summary

    def wait_for_completion(self):
        """
        Wait for the assistant run to complete and handle any required actions.
        
        This method polls the run status every 5 seconds until completion.
        This test version is named 'wait_for_completion' vs 'wait_for_run_completion'
        in main.py and uses standard API calls.
        
        Handles two main run statuses:
        - "completed": Processes the final message
        - "requires_action": Executes required functions and continues
        """
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    def run_steps(self):
        """
        Retrieve detailed information about the run steps.
        
        This provides debugging and monitoring information about
        what the assistant did during the run. Test version uses standard API calls.
        
        Returns:
            list: List of run step objects containing execution details
        """
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data


def main():
    """
    Main function for the test version of the News Summarizer application.
    
    This function creates and runs the Streamlit web application for testing
    new features and configurations. It has enhanced assistant instructions
    compared to the main version.
    
    Key differences from main.py:
    - More detailed assistant instructions for better summarization
    - Uses gpt-3.5-turbo-16k model for larger context
    - May include experimental UI elements or error handling
    
    The application flow:
    1. Display a form for topic input
    2. Create an assistant with enhanced news summarization capabilities
    3. Create a conversation thread
    4. Process the user's request for news summarization
    5. Display the generated summary and run steps
    """
    # Create an instance of the AssistantManager
    manager = AssistantManager()

    # Streamlit interface setup
    st.title("News Summarizer (Test Version)")
    st.markdown("🧪 Test version with enhanced capabilities - Enter a topic to get AI-powered news summaries")

    # Create a form for user input
    with st.form(key="user_input_form"):
        instructions = st.text_input(
            "Enter topic:", 
            placeholder="e.g., bitcoin, technology, sports"
        )
        submit_button = st.form_submit_button(label="Run Assistant")

        if submit_button:
            # Validate input
            if not instructions.strip():
                st.error("Please enter a topic to search for news.")
                return
                
            # Show progress indicator
            with st.spinner("Processing with enhanced assistant..."):
                # Create the assistant with enhanced summarization capabilities
                manager.create_assistant(
                    name="News Summarizer",
                    instructions="You are a personal article summarizer Assistant who knows how to take a list of article's titles and descriptions and then write a short summary of all the news articles",
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": "get_news",
                                "description": "Get the list of articles/news for the given topic",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "topic": {
                                            "type": "string",
                                            "description": "The topic for the news, e.g. bitcoin",
                                        }
                                    },
                                    "required": ["topic"],
                                },
                            },
                        }
                    ],
                )
                
                # Create a conversation thread
                manager.create_thread()

                # Add the user's message to the thread
                manager.add_message_to_thread(
                    role="user", 
                    content=f"summarize the news on this topic {instructions}?"
                )
                
                # Start the assistant run
                manager.run_assistant(instructions="Summarize the news")

                # Wait for completion and process the results
                manager.wait_for_completion()

            # Display the results
            summary = manager.get_summary()
            
            if summary:
                st.subheader("📰 Enhanced News Summary")
                st.write(summary)
                
                # Show run steps for debugging (optional)
                with st.expander("🔍 View Run Steps (Debug Info)"):
                    st.text("Run Steps:")
                    st.code(manager.run_steps(), line_numbers=True)
            else:
                st.error("Could not generate summary. Please try again.")


if __name__ == "__main__":
    main()