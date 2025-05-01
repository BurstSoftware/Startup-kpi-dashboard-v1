import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
from io import BytesIO

# Streamlit page configuration
st.set_page_config(page_title="Startup KPI Dashboard", layout="wide")

# Google Sheets setup
def load_data_from_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Startup_KPI_Data").sheet1  # Replace with your sheet name
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Function to generate downloadable CSV
def get_table_download_link(df, filename="kpi_report.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV Report</a>'
    return href

# Load data
try:
    df = load_data_from_gsheets()
except Exception as e:
    st.error(f"Error loading data from Google Sheets: {e}")
    df = pd.DataFrame()  # Fallback empty DataFrame

# Sidebar for KPI selection and filters
st.sidebar.header("KPI Filters")
available_kpis = ['MRR', 'DAU', 'Churn_Rate', 'Burn_Rate', 'Revenue_Growth']
selected_kpis = st.sidebar.multiselect("Select KPIs to Display", available_kpis, default=available_kpis)

# Threshold settings for alerts
st.sidebar.header("Alert Thresholds")
burn_rate_threshold = st.sidebar.number_input("Burn Rate Alert Threshold ($)", value=2000)
churn_rate_threshold = st.sidebar.number_input("Churn Rate Alert Threshold (%)", value=5.0)

# Main dashboard
st.title("Startup KPI Dashboard")
st.markdown("Monitor key performance indicators with real-time data and trend analysis.")

if not df.empty:
    # Filter data based on selected KPIs
    df_display = df[['Date'] + selected_kpis]

    # KPI Overview Cards
    st.subheader("KPI Overview")
    cols = st.columns(len(selected_kpis))
    latest_data = df.iloc[-1]
    for idx, kpi in enumerate(selected_kpis):
        with cols[idx]:
            value = latest_data[kpi]
            st.metric(label=kpi, value=f"{value:,.2f}")

    # Alerts for KPI thresholds
    st.subheader("Alerts")
    if 'Burn_Rate' in selected_kpis and latest_data['Burn_Rate'] > burn_rate_threshold:
        st.warning(f"⚠️ High Burn Rate: {latest_data['Burn_Rate']:,.2f} exceeds threshold of {burn_rate_threshold:,.2f}")
    if 'Churn_Rate' in selected_kpis and latest_data['Churn_Rate'] > churn_rate_threshold:
        st.warning(f"⚠️ High Churn Rate: {latest_data['Churn_Rate']:,.2f}% exceeds threshold of {churn_rate_threshold:,.2f}%")

    # Visual Dashboards with Trend Analysis
    st.subheader("Trend Analysis")
    for kpi in selected_kpis:
        fig = px.line(df, x='Date', y=kpi, title=f"{kpi} Trend Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title=kpi)
        st.plotly_chart(fig, use_container_width=True)

    # Exportable KPI Report
    st.subheader("Export Report")
    st.markdown(get_table_download_link(df_display), unsafe_allow_html=True)
else:
    st.warning("No data available. Please check your Google Sheets connection.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Data Source: Google Sheets | © 2025 Startup KPI Dashboard")
