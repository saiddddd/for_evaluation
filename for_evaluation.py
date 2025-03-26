import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")

    st.sidebar.header("Select Filters")
    kpi_name = st.sidebar.selectbox("Select KPI Name", df['kpi_name'].unique())
    kpi_category = st.sidebar.selectbox("Select KPI Category", df['kpi_category'].unique())
    level = st.sidebar.selectbox("Select Level", df['level'].unique())

    available_locations = df[df['level'] == level]['location'].unique()
    location = st.sidebar.selectbox("Select Location", available_locations)

    df_filtered = df[
        (df['kpi_name'] == kpi_name) &
        (df['kpi_category'] == kpi_category) &
        (df['level'] == level) &
        (df['location'] == location)
    ].copy()

    if 'yearweek' in df_filtered.columns:
        df_filtered['time'] = pd.to_datetime(df_filtered['yearweek'].astype(str) + '-1', format='%G%V-%u', errors='coerce')


    df_significant = df_filtered[df_filtered['significant_result'].isin(["Increase", "Decrease"])].copy()

    st.header(f"Significant Changes for {location} - {kpi_name}")

    plt.figure(figsize=(14, 6))
    color_map = {'Increase': 'red', 'Decrease': 'green'}

    for result, color in color_map.items():
        subset = df_significant[df_significant['significant_result'] == result]
        if not subset.empty:
            plt.scatter(subset['time'], subset['kpi_value'], color=color, s=50, label=f'Alert {result}')

    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xlabel("Time")
    plt.ylabel(kpi_name)
    plt.title(f"Significant Changes in {kpi_name} for {location}")
    plt.legend()
    plt.grid(True)

    st.pyplot(plt)
