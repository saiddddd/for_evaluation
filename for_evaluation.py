import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")

    st.sidebar.header("Select Filters")

    kpi_category = st.sidebar.selectbox("Select KPI Category", df['kpi_category'].dropna().unique())
    available_kpi_names = df[df['kpi_category'] == kpi_category]['kpi_name'].dropna().unique()
    kpi_name = st.sidebar.selectbox("Select KPI Name", available_kpi_names)

    available_levels = df[
        (df['kpi_category'] == kpi_category) & 
        (df['kpi_name'] == kpi_name)
    ]['level'].dropna().unique()
    level = st.sidebar.selectbox("Select Level", available_levels)

    available_locations = df[
        (df['kpi_category'] == kpi_category) & 
        (df['kpi_name'] == kpi_name) & 
        (df['level'] == level)
    ]['location'].dropna().unique()
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
        "- 🟩 (Alert) Indicates a **Improve**\n"
        "- 🟥 (Alert) Indicates an **Degrade**",
        icon="⚠️"
    )


    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_filtered['time'], y=df_filtered['kpi_value'],
                             mode='lines+markers', name='Actual Value', line=dict(color='blue')))
    
    fig.add_trace(go.Scatter(x=df_filtered['time'], y=df_filtered['valid_value'],
                             mode='lines+markers', name='Valid Value', line=dict(color='black')))
    
    if 'lb' in df_filtered.columns and 'ub' in df_filtered.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([df_filtered['time'], df_filtered['time'][::-1]]),
            y=pd.concat([df_filtered['ub'], df_filtered['lb'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 0, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Confidence Interval',
            showlegend=True
        ))

    if 'alert_status' in df_filtered.columns:
        df_filtered['alert_status'] = df_filtered['alert_status'].astype(str).str.lower()
        color_map = {'degrade': 'red', 'improve': 'green'}
        for result, color in color_map.items():
            subset = df_filtered[df_filtered['alert_status'] == result]
            if not subset.empty:
                fig.add_trace(go.Scatter(
                    x=subset['time'], y=subset['kpi_value'],
                    mode='markers',
                    marker=dict(color=color, size=10),
                    name=f'Alert {result.capitalize()}'
                ))

    fig.update_layout(
        title=f"{kpi_name} Over Time for {location}",
        xaxis_title="Time",
        yaxis_title=kpi_name,
        xaxis=dict(tickangle=45),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=20, r=20, t=50, b=100),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descriptive Statistics")
    stats_cols = ['kpi_value', 'valid_value', 'lb', 'ub']
    stats_available = [col for col in stats_cols if col in df_filtered.columns]
    st.write(df_filtered[stats_available].describe())

    st.subheader("Filtered Data Preview")
    extra_cols = ['alert_description_percentage', 'count_alert', 'alert_status']
    table_cols = stats_available + [col for col in extra_cols if col in df_filtered.columns]
    st.write(df_filtered[table_cols])


    st.subheader("Summary Table")
    summary_cols = ['level', 'location', 'kpi_category', 'kpi_name', 'alert_description_percentage']
    summary_data = df_filtered[summary_cols].drop_duplicates()
    st.dataframe(summary_data, use_container_width=True)
