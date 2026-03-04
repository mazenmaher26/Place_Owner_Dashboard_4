import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Owner Dashboard", layout="wide")

# --- MOCK DATA ENGINE ---
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-03-01", periods=365, freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Visits': np.random.randint(100, 500, size=365),
        'Saves': np.random.randint(10, 60, size=365),
        'Directions': np.random.randint(20, 100, size=365),
        'Calls': np.random.randint(5, 40, size=365),
        'Orders': np.random.randint(30, 150, size=365),
        'Chat_Queries': np.random.randint(50, 200, size=365),
        'Bot_Success_Rate': np.random.uniform(70, 95, size=365),
        'Review_Sentiment': np.random.choice(
            ['Positive', 'Negative'], 
            size=365, 
            p=[0.8, 0.2]
        )
    })
    return data

df_raw = load_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🏙️ AroundU")
    # st.caption("Beni Suef Business Intelligence")

    selected = option_menu(
        "Main Menu", 
        ["Dashboard", "Customer Insights", "Operations", "Location Logic"],
        icons=['speedometer2', 'chat-heart', 'clock-history', 'geo-alt'], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"background-color": "#1e1e1e"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

    st.markdown("---")
    st.write("Logged in as: **Puffy and Fluffy**")

    st.markdown("### 📅 Select Date Range")
    min_date = df_raw['Date'].min().to_pydatetime()
    max_date = df_raw['Date'].max().to_pydatetime()

    date_range = st.date_input(
        "Choose period:",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date
    )

# =========================
# FILTER LOGIC
# =========================
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = df_raw[
        (df_raw['Date'] >= start_date) & 
        (df_raw['Date'] <= end_date)
    ]

    period_days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=period_days)
    prev_end = start_date - timedelta(days=1)

    prev_df = df_raw[
        (df_raw['Date'] >= prev_start) & 
        (df_raw['Date'] <= prev_end)
    ]
else:
    st.warning("Please select a valid date range in the sidebar.")
    st.stop()

# =========================
# 1️⃣ DASHBOARD
# =========================
if selected == "Dashboard":
    st.title("📊 Business Performance Overview")

    m1, m2, m3, m4 = st.columns(4)

    def get_delta_val(col):
        if prev_df.empty:
            return None
        curr = filtered_df[col].sum()
        prev = prev_df[col].sum()
        if prev == 0:
            return "0%"
        diff = ((curr - prev) / prev) * 100
        return f"{int(diff)}%"

    m1.metric("Total Visits", int(filtered_df['Visits'].sum()), get_delta_val('Visits'))
    m2.metric("Place Saved", int(filtered_df['Saves'].sum()), get_delta_val('Saves'))
    m3.metric("Direction Clicks", int(filtered_df['Directions'].sum()), get_delta_val('Directions'))
    m4.metric("Call Clicks", int(filtered_df['Calls'].sum()), get_delta_val('Calls'))

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🚀 Growth Analysis (Current vs Previous Period)")

        metrics = ['Visits', 'Orders', 'Saves', 'Calls']
        curr_vals = [filtered_df[m].sum() for m in metrics]
        prev_vals = [prev_df[m].sum() for m in metrics]

        growth_data = pd.DataFrame({
            'Metric': metrics * 2,
            'Value': curr_vals + prev_vals,
            'Period': ['Selected Period'] * 4 + ['Previous Period'] * 4
        })

        fig_growth = px.bar(
            growth_data,
            x='Metric',
            y='Value',
            color='Period',
            barmode='group',
            text_auto='.2s',
            color_discrete_map={
                'Selected Period': '#ff4b4b',
                'Previous Period': '#6C757D'
            },
            template="plotly_dark"
        )

        st.plotly_chart(fig_growth, use_container_width=True)

    with col_right:
        st.subheader("🤖 Chatbot Stats")
        st.metric("Bot Resolution Rate", f"{filtered_df['Bot_Success_Rate'].mean():.1f}%")

        query_types = pd.DataFrame({
            'Type': ['Menu', 'Hours', 'Location', 'Pricing'],
            'Val': [40, 30, 20, 10]
        })

        fig_pie = px.pie(
            query_types,
            values='Val',
            names='Type',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

# =========================
# 2️⃣ CUSTOMER INSIGHTS
# =========================
elif selected == "Customer Insights":
    st.title("🤖 Customer & Review Analysis")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Customer Reviews: Positive vs Negative")

        fig_reviews = px.bar(
            filtered_df,
            x='Date',
            y='Visits',
            color='Review_Sentiment',
            color_discrete_map={
                'Positive': '#28A745',
                'Negative': '#DC3545'
            },
            barmode='stack',
            template="plotly_dark"
        )

        st.plotly_chart(fig_reviews, use_container_width=True)

    with c2:
        st.subheader("Review Ratings Distribution")

        ratings = np.random.choice(
            [1, 2, 3, 4, 5],
            size=100,
            p=[0.05, 0.05, 0.1, 0.3, 0.5]
        )

        fig_rate = px.histogram(
            x=ratings,
            nbins=5,
            color_discrete_sequence=['#FFC107'],
            template="plotly_dark"
        )

        fig_rate.update_layout(
            xaxis_title="Star Rating",
            yaxis_title="Count"
        )

        st.plotly_chart(fig_rate, use_container_width=True)

# =========================
# 3️⃣ OPERATIONS
# =========================
elif selected == "Operations":
    st.title("⏰ Operational Efficiency")

    hours = [f"{i}:00" for i in range(24)]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    heat_data = np.random.randint(10, 100, size=(7, 24))

    fig_heat = px.imshow(
        heat_data,
        x=hours,
        y=days,
        color_continuous_scale='GnBu',
        aspect="auto",
        template="plotly_dark"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

# =========================
# 4️⃣ LOCATION LOGIC
# =========================
elif selected == "Location Logic":
    st.title("📍 Location Analysis: Beni Suef")

    BS_LAT, BS_LON = 29.0661, 31.0994

    map_data = pd.DataFrame({
        'lat': np.random.uniform(BS_LAT - 0.015, BS_LAT + 0.015, size=200),
        'lon': np.random.uniform(BS_LON - 0.015, BS_LON + 0.015, size=200),
        'Intensity': np.random.randint(1, 100, size=200)
    })

    fig_map = px.density_mapbox(
        map_data,
        lat='lat',
        lon='lon',
        z='Intensity',
        radius=15,
        center=dict(lat=BS_LAT, lon=BS_LON),
        zoom=12.5,
        mapbox_style="open-street-map",
        height=700
    )

    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig_map, use_container_width=True)
