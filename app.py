import streamlit as st
import pandas as pd
import plotly.express as px
from processor import load_wdi_data
from interpreter_chain import generate_story
import os

# Page Config
st.set_page_config(
    page_title="Economic Interpreter",
    page_icon="🌍",
    layout="wide"
)

# Header
st.title("🌍 Economic Interpreter: From Data to Narrative")
st.markdown("""
This tool combines **World Development Indicators (WDI)** data with **Historical News (GDELT)** 
to explain economic shifts using AI.
""")

# Load Data
@st.cache_data
def get_data():
    try:
        return load_wdi_data()
    except Exception as e:
        st.error(f"Error loading WDI Data: {e}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.warning("No data available. Please run data preprocessing first.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Configuration")

# Country Selection
countries = sorted(df['Country Name'].unique())
selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index("United States") if "United States" in countries else 0)

# Indicator Selection
indicators = sorted(df['Indicator Name'].unique())
selected_indicator = st.sidebar.selectbox("Select Indicator", indicators, index=0)

# Filter Data
country_data = df[
    (df['Country Name'] == selected_country) & 
    (df['Indicator Name'] == selected_indicator)
].sort_values('Year')

# Get Country Code for Retrieval
country_code = country_data['Country Code'].iloc[0] if not country_data.empty else 'Unknown'

# Metric Cards
# Display latest available value and YoY change
if not country_data.empty:
    latest = country_data.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Year", int(latest['Year']))
    col1.metric("Value", f"{latest['Value']:.2f}%")
    col3.metric("YoY Change", f"{latest['YoY_Change']:.2f}%", delta_color="inverse")

# Main Chart
st.subheader(f"{selected_indicator} Trend in {selected_country}")
fig = px.line(
    country_data, 
    x="Year", 
    y="Value", 
    markers=True,
    title=f"{selected_indicator} over Time",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# Analysis Section
st.divider()
st.subheader("AI Analysis")

# Year Selection for Analysis
years = sorted(country_data['Year'].astype(int).unique(), reverse=True)
selected_year = st.selectbox("Select a Year to Analyze", years)

# Get specific data point
row = country_data[country_data['Year'] == selected_year]

if not row.empty:
    val = row.iloc[0]['Value']
    delta = row.iloc[0]['YoY_Change']
    
    st.info(f"In **{selected_year}**, {selected_indicator} was **{val:.2f}%** (Change: {delta:.2f}%).")
    
    if st.button("Explain this Shift"):
        with st.spinner("Retrieving news and generating explanation..."):
            try:
                story = generate_story(
                    country=selected_country,
                    year=int(selected_year),
                    indicator_name=selected_indicator,
                    delta=delta,
                    country_code=country_code
                )
                
                st.markdown("###  The Story Behind the Numbers")
                st.write(story)
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ The model is currently rate-limited. Please try again in a few minutes.")
