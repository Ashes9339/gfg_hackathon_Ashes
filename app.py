import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from google import genai
import json
import os
from dotenv import load_dotenv


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)


# ---------------- LOAD API KEY ----------------

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# ---------------- HEADER ----------------

st.title("📊 Conversational AI Business Intelligence Dashboard")

st.markdown("""
Ask questions about your dataset and the system will automatically:

• Generate SQL queries  
• Analyze the data  
• Build visualizations  
""")


# ---------------- SIDEBAR ----------------

st.sidebar.title("Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV Dataset (optional)",
    type=["csv"]
)

question = st.sidebar.text_input("Ask a question")

generate = st.sidebar.button("Generate Dashboard")


# ---------------- DATASET LOADING ----------------

if uploaded_file is not None:

    df_uploaded = pd.read_csv(uploaded_file)

    conn = sqlite3.connect(":memory:")
    df_uploaded.to_sql("data", conn, index=False, if_exists="replace")

    dataset_name = "data"
    columns = ", ".join(df_uploaded.columns)

    total_rows = len(df_uploaded)

    df_preview = df_uploaded.head(10)

    st.success("Using uploaded dataset")

else:

    conn = sqlite3.connect("customers.db")

    total_rows = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM customers",
        conn
    )["count"][0]

    df_preview = pd.read_sql_query(
        "SELECT * FROM customers LIMIT 10",
        conn
    )

    dataset_name = "customers"
    columns = ", ".join(df_preview.columns)

    st.info("Using default dataset")


# ---------------- DATASET INFO ----------------

st.subheader("Dataset Information")

col1, col2 = st.columns(2)

with col1:
    st.metric("Rows", total_rows)

with col2:
    st.metric("Columns", len(df_preview.columns))


# ---------------- DATASET PREVIEW ----------------

st.subheader("Dataset Preview")

st.caption("Showing first 10 rows of the dataset")

st.dataframe(df_preview, width="stretch")


# ---------------- GEMINI CACHE ----------------

@st.cache_data(ttl=3600)
def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response


# ---------------- DATABASE QUERY ----------------

@st.cache_data
def run_query(sql_query):
    return pd.read_sql_query(sql_query, conn)


# ---------------- MAIN LOGIC ----------------

if generate:

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    prompt = f"""
You are a data analyst.

Database table: {dataset_name}

Columns:
{columns}

User question:
{question}

Return ONLY valid JSON.

The SQL can return:
1) Two columns (category and value) for charts
OR
2) A single aggregated value (like average, median, count).

Use SQLite compatible SQL only.

Format:

{{
"sql":"SQL_QUERY"
}}
"""

    response = None

    try:

        with st.spinner("Analyzing data with AI..."):

            response = ask_gemini(prompt)

        text = response.text.strip()

        json_start = text.find("{")
        json_end = text.rfind("}") + 1

        json_text = text[json_start:json_end]

        result = json.loads(json_text)

        sql = result.get("sql")

        st.subheader("Generated SQL")
        st.code(sql)

        df = run_query(sql)

        if df.empty:
            st.warning("Query returned no results.")
            st.stop()

        st.subheader("Query Result")
        st.dataframe(df, width="stretch")


        # ---------------- METRIC HANDLING ----------------

        if df.shape[1] == 1:

            metric_name = df.columns[0].replace("_"," ").title()
            metric_value = df.iloc[0,0]

            st.subheader("Result")
            st.metric(metric_name, metric_value)
            st.stop()


        st.divider()


        # ---------------- VISUALIZATION ----------------

        st.subheader("📈 Visualization")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Bar Chart")

            fig_bar = px.bar(
                df,
                x=df.columns[0],
                y=df.columns[1]
            )

            st.plotly_chart(fig_bar, width="stretch")


        with col2:

            st.subheader("Pie Chart")

            fig_pie = px.pie(
                df,
                names=df.columns[0],
                values=df.columns[1]
            )

            st.plotly_chart(fig_pie, width="stretch")


        st.subheader("Line Chart")

        fig_line = px.line(
            df,
            x=df.columns[0],
            y=df.columns[1]
        )

        st.plotly_chart(fig_line, width="stretch")


    except Exception as e:

        st.error("Something went wrong.")

        if response:
            st.write("Gemini response:")
            st.write(response.text)

        st.write("Error details:", e)