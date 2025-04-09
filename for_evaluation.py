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

    kpi_category = st.sidebar.selectbox("Select KPI Category", df['kpi_category'].unique())

    available_kpi_names = df[df['kpi_category'] == kpi_category]['kpi_name'].unique()
    kpi_name = st.sidebar.selectbox("Select KPI Name", available_kpi_names)

    available_levels = df[(df['kpi_category'] == kpi_category) & (df['kpi_name'] == kpi_name)]['level'].unique()
    level = st.sidebar.selectbox("Select Level", available_levels)

    available_locations = df[
        (df['kpi_category'] == kpi_category) & 
        (df['kpi_name'] == kpi_name) & 
        (df['level'] == level)
    ]['location'].unique()
    location = st.sidebar.selectbox("Select Location", available_locations)

    df_filtered = df[
        (df['kpi_category'] == kpi_category) &
        (df['kpi_name'] == kpi_name) &
        (df['level'] == level) &
        (df['location'] == location)
    ].copy()

    if 'yearweek' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['yearweek'].notna()]
        
        df_filtered['yearweek'] = df_filtered['yearweek'].astype(str).str.zfill(6)
        df_filtered['year'] = df_filtered['yearweek'].str[:4].astype(int)
        df_filtered['week'] = df_filtered['yearweek'].str[4:].astype(int)

        df_filtered = df_filtered[(df_filtered['week'] > 0) & (df_filtered['week'] <= 53)]

        df_filtered['time'] = pd.to_datetime(df_filtered['year'].astype(str) + '-W' + df_filtered['week'].astype(str) + '-1', format='%Y-W%W-%w', errors='coerce')

        df_filtered = df_filtered[df_filtered['time'].notna() & (df_filtered['time'].dt.year >= 2000)]

    st.header(f"Visualization for {location} - {kpi_name}")

    
    st.warning(
        "⚠ **Caution:** The Y-axis scale might be relatively small, making variations appear visually significant. "
        "However, statistical tests such as T-tests should be used to determine true statistical significance.\n\n"
        "**Legend:**\n"
        "- 🟩 Alert 1 Indicates a **decrease**\n"
        "- 🟥 Alert 2 Indicates an **increase**",
        icon="⚠️"
    )

    st.markdown(
        """
        <style>
        .stMarkdown p {
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )



    plt.figure(figsize=(14, 6))
    sns.lineplot(data=df_filtered, x='time', y='kpi_value', label='Actual Value', color='blue')
    sns.lineplot(data=df_filtered, x='time', y='valid_value', label='Valid Value', color='black')

    if 'lb' in df_filtered.columns and 'ub' in df_filtered.columns:
        plt.fill_between(df_filtered['time'], df_filtered['lb'], df_filtered['ub'], color='blue', alpha=0.2, label='Confidence Interval')

    if 'status_alert' in df_filtered.columns:
        color_map = {'degrade': 'red', 'improve': 'green'}
        for result, color in color_map.items():
            subset = df_filtered[df_filtered['status_alert'] == result]
            plt.scatter(subset['time'], subset['kpi_value'], color=color, s=50, label=f'Alert {result} (statistical significance)')

    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xlabel("Time")
    plt.ylabel(kpi_name)
    plt.title(f"{kpi_name} Over Time for {location}")
    plt.legend()
    plt.grid(True)

    st.pyplot(plt)

    st.subheader("Descriptive Statistics")
    st.write(df_filtered[['kpi_value', 'valid_value', 'lb', 'ub']].describe())
