import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df[['date', 'level', 'location', 'raw_value', 'initial_projection', 'latest_projection']]

    # Paksa parsing format MM/DD/YYYY
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y', errors='coerce')
    df = df[df['date'].notna()]
    df = df.sort_values(by='date')

    st.sidebar.success("File uploaded successfully!")
    st.sidebar.header("Select Filters")

    level = st.sidebar.selectbox("Select Level", df['level'].dropna().unique())
    available_locations = df[df['level'] == level]['location'].dropna().unique()
    location = st.sidebar.selectbox("Select Location", available_locations)

    df_filtered = df[(df['level'] == level) & (df['location'] == location)].copy()
    df_filtered = df_filtered.sort_values(by='date')

    if not df_filtered.empty:
        min_date = df_filtered['date'].min().date()
        max_date = df_filtered['date'].max().date()

        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['date'] >= pd.to_datetime(start_date)) & 
                (df_filtered['date'] <= pd.to_datetime(end_date))
            ]

    st.header(f"Adaptive Projection for {location}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['raw_value'],
                             mode='lines+markers', name='Raw Value', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['initial_projection'],
                             mode='lines+markers', name='Initial Projection', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['latest_projection'],
                             mode='lines+markers', name='Latest Projection', line=dict(color='green')))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Payload (TByte)",
        title=f"Payload Adaptive Projection for {location}",
        hovermode="x unified",
        height=500,
        margin=dict(t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descriptive Statistics")
    st.write(df_filtered[['raw_value', 'initial_projection', 'latest_projection']].describe())

    st.subheader("Filtered Data")
    st.dataframe(df_filtered[['date', 'level', 'location', 'raw_value', 'initial_projection', 'latest_projection']])
