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
    location = st.sidebar.selectbox("Select Location", df['location'].unique())
    

    df_filtered = df[
        (df['kpi_name'] == kpi_name) &
        (df['kpi_category'] == kpi_category) &
        (df['level'] == level) &
        (df['location'] == location)
    ]
    

    df_filtered['granularity'] = df_filtered['granularity'].astype(str)
    if 'yearweek' in df_filtered.columns:
        df_filtered['time'] = pd.to_datetime(df_filtered['yearweek'].astype(str) + '0', format='%Y%W%w')
    else:
        df_filtered['time'] = pd.to_datetime(df_filtered['date'], errors='coerce')
    

    st.header(f"Visualization for {location} - {kpi_name}")
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=df_filtered, x='time', y='kpi_value', label='Actual Value', color='blue')
    sns.lineplot(data=df_filtered, x='time', y='valid_value', label='Valid Value', color='black')
    

    if 'lb' in df_filtered.columns and 'ub' in df_filtered.columns:
        plt.fill_between(df_filtered['time'], df_filtered['lb'], df_filtered['ub'], color='blue', alpha=0.2, label='Confidence Interval')
    

    if 'significant_result' in df_filtered.columns:
        color_map = {'1': 'red', '2': 'green'}
        for result, color in color_map.items():
            subset = df_filtered[df_filtered['significant_result'] == result]
            plt.scatter(subset['time'], subset['kpi_value'], color=color, s=50, label=f'Alert {result}')
    
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    plt.xlabel("Time")
    plt.ylabel(kpi_name)
    plt.title(f"{kpi_name} Over Time for {location}")
    plt.legend()
    plt.grid(True)
    
    st.pyplot(plt)
