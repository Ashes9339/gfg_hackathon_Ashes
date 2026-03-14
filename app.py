import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from google import genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

st.title("Conversational AI Business Intelligence Dashboard")

st.write("Ask questions about customer shopping behavior")

question = st.text_input("Enter your question")

if st.button("Generate Dashboard"):

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    prompt = f"""
You are a data analyst.

Database table: customers

Columns:
age, monthly_income, daily_internet_hours,
monthly_online_orders, monthly_store_visits,
avg_online_spend, avg_store_spend,
gender, city_tier, shopping_preference

User question:
{question}

Return ONLY valid JSON.

The SQL must return TWO columns:
1) category column
2) numeric value column

Example:
SELECT city_tier, COUNT(*) as value FROM customers GROUP BY city_tier

Format:

{{
"sql":"SQL_QUERY",
"chart":"bar|line|pie"
}}
"""

    response = None

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Extract JSON safely
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        json_text = text[json_start:json_end]

        result = json.loads(json_text)

        sql = result["sql"]
        chart = result["chart"]

        st.subheader("Generated SQL")
        st.code(sql)

        conn = sqlite3.connect("customers.db")

        df = pd.read_sql_query(sql, conn)

        conn.close()

        if df.empty:
            st.warning("Query returned no results.")
            st.stop()

        st.subheader("Data Preview")
        st.dataframe(df)

        # Check column count before chart
        if len(df.columns) < 2:

            st.warning("Not enough columns for chart. Showing table only.")
            st.dataframe(df)

        else:

            if chart == "bar":
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])

            elif chart == "line":
                fig = px.line(df, x=df.columns[0], y=df.columns[1])

            elif chart == "pie":
                fig = px.pie(df, names=df.columns[0], values=df.columns[1])

            else:
                st.warning("Unknown chart type. Showing table.")
                st.dataframe(df)
                st.stop()

            st.subheader("Visualization")
            st.plotly_chart(fig)

    except Exception as e:

        st.error("Something went wrong.")

        if response:
            st.write("Gemini response:")
            st.write(response.text)

        st.write("Error details:", e)