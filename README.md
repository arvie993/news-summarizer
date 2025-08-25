# News Summarizer

<!-- Image reference removed due to missing asset -->

A Python-based news summarization application that uses OpenAI's GPT models and the News API to fetch and summarize news articles on any given topic.

## Features

- Fetches latest news articles using News API
- Uses OpenAI's Assistant API to summarize news content
- Interactive Streamlit web interface
- Supports any news topic or keyword

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd news-summarizer
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
NEWS_API_KEY=your_news_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## API Keys Required

- **News API**: Get your free API key from [NewsAPI.org](https://newsapi.org/)
- **OpenAI API**: Get your API key from [OpenAI Platform](https://platform.openai.com/)

## Usage

### Running the Streamlit App

```bash
streamlit run main.py
```

This will start a web interface where you can:
1. Enter a topic of interest
2. Click "Run Assistant" to fetch and summarize news
3. View the AI-generated summary of recent articles

### Running Tests

```bash
python test.py
```

## Files Description

- `main.py`: Main application with Streamlit interface and OpenAI Assistant integration
- `test.py`: Test script for the news summarization functionality
- `requirements.txt`: Python dependencies
- `.env`: Environment variables for API keys (not included in repository)
- `.gitignore`: Git ignore file to exclude sensitive files and directories

## How it Works

1. **News Fetching**: Uses News API to retrieve the latest 5 articles for a given topic
2. **AI Processing**: Utilizes OpenAI's Assistant API with function calling to process news data
3. **Summarization**: The AI assistant analyzes articles and provides concise summaries
4. **Web Interface**: Streamlit provides an easy-to-use web interface for interaction

## Dependencies

- `python-dotenv`: For environment variable management
- `openai`: OpenAI API client
- `requests`: HTTP requests for News API
- `streamlit`: Web interface framework

## Note

Make sure to keep your API keys secure and never commit them to version control. The `.env` file is already included in `.gitignore` for this purpose.
