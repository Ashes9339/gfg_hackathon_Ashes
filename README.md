# Conversational AI Business Intelligence Dashboard

This project converts natural language queries into SQL queries and generates visual dashboards.

## Tech Stack

- Python
- Streamlit
- SQLite
- Plotly
- Google Gemini API

## Features

- Natural language → SQL conversion
- Automatic data visualization
- Interactive dashboard
- AI-powered analytics

## Setup

1.Install dependencies:

 pip install -r requirements.txt

2.Create `.env` file;

Then put this into the .env file:

        GEMINI_API_KEY=your_api_key


3.Run this to the terminal:

    a.python clean_data.py
    b.python database.py
    c.streamlit run app.py / python -m streamlit run app.py