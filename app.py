import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Road Accident Analysis Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "road_accidents.csv")
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["year"] = df["date"].dt.year
    df["hour"] = df["time"].str[:2].astype(int)
    return df


# ── Load data ─────────────────────────────────────────────────────────────────

df_all = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.title("Filters")

date_min = df_all["date"].min().date()
date_max = df_all["date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range", value=(date_min, date_max), min_value=date_min, max_value=date_max
)

regions = st.sidebar.multiselect(
    "Region", options=sorted(df_all["region"].unique()), default=[]
)

severities = st.sidebar.multiselect(
    "Severity", options=["Fatal", "Serious", "Slight"], default=[]
)

weather_filter = st.sidebar.multiselect(
    "Weather", options=sorted(df_all["weather"].unique()), default=[]
)

road_type_filter = st.sidebar.multiselect(
    "Road Type", options=sorted(df_all["road_type"].unique()), default=[]
)

# Apply filters
df = df_all.copy()
if len(date_range) == 2:
    df = df[(df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])]
if regions:
    df = df[df["region"].isin(regions)]
if severities:
    df = df[df["severity"].isin(severities)]
if weather_filter:
    df = df[df["weather"].isin(weather_filter)]
if road_type_filter:
    df = df[df["road_type"].isin(road_type_filter)]


# ── Color palette ─────────────────────────────────────────────────────────────

SEVERITY_COLORS = {"Fatal": "#e74c3c", "Serious": "#f39c12", "Slight": "#2ecc71"}

# ── Title ─────────────────────────────────────────────────────────────────────

st.title("Road Accident Analysis Dashboard")
st.caption(f"Analyzing **{len(df):,}** accidents from {date_min} to {date_max}  |  Data also available in Snowflake: ROAD_ACCIDENTS_DB.ANALYTICS.ACCIDENTS")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: KPI METRICS
# ══════════════════════════════════════════════════════════════════════════════

total_accidents = len(df)
total_fatalities = int(df["num_fatalities"].sum())
total_injuries = int(df["num_injuries"].sum())
total_casualties = int(df["num_casualties"].sum())
fatality_rate = round((total_fatalities / total_casualties * 100), 2) if total_casualties > 0 else 0
avg_casualties = round(df["num_casualties"].mean(), 2) if total_accidents > 0 else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Accidents", f"{total_accidents:,}")
k2.metric("Total Fatalities", f"{total_fatalities:,}")
k3.metric("Total Injuries", f"{total_injuries:,}")
k4.metric("Total Casualties", f"{total_casualties:,}")
k5.metric("Fatality Rate", f"{fatality_rate}%")
k6.metric("Avg Casualties/Accident", f"{avg_casualties}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ACCIDENT FREQUENCY TRENDS
# ══════════════════════════════════════════════════════════════════════════════

st.header("Accident Frequency Trends")

col_a, col_b = st.columns(2)

with col_a:
    monthly = df.groupby("month").size().reset_index(name="accidents")
    fig_monthly = px.line(
        monthly, x="month", y="accidents",
        title="Monthly Accident Trend",
        labels={"month": "Month", "accidents": "Number of Accidents"},
    )
    fig_monthly.update_traces(line_color="#3498db", line_width=2)
    fig_monthly.update_layout(hovermode="x unified")
    st.plotly_chart(fig_monthly, use_container_width=True)

with col_b:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily = df.groupby("day_of_week").size().reset_index(name="accidents")
    daily["day_of_week"] = pd.Categorical(daily["day_of_week"], categories=day_order, ordered=True)
    daily = daily.sort_values("day_of_week")
    fig_daily = px.bar(
        daily, x="day_of_week", y="accidents",
        title="Accidents by Day of Week",
        labels={"day_of_week": "Day", "accidents": "Accidents"},
        color_discrete_sequence=["#2980b9"],
    )
    st.plotly_chart(fig_daily, use_container_width=True)

hourly = df.groupby("hour").size().reset_index(name="accidents")
fig_hourly = px.area(
    hourly, x="hour", y="accidents",
    title="Accidents by Hour of Day",
    labels={"hour": "Hour (24h)", "accidents": "Accidents"},
    color_discrete_sequence=["#8e44ad"],
)
fig_hourly.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_hourly, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: SEVERITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

st.header("Severity Analysis")

col_s1, col_s2 = st.columns(2)

with col_s1:
    sev_counts = df["severity"].value_counts().reset_index()
    sev_counts.columns = ["severity", "count"]
    fig_sev_pie = px.pie(
        sev_counts, names="severity", values="count",
        title="Severity Distribution",
        color="severity", color_discrete_map=SEVERITY_COLORS,
        hole=0.4,
    )
    st.plotly_chart(fig_sev_pie, use_container_width=True)

with col_s2:
    sev_monthly = df.groupby(["month", "severity"]).size().reset_index(name="count")
    fig_sev_trend = px.area(
        sev_monthly, x="month", y="count", color="severity",
        title="Severity Trend Over Time",
        color_discrete_map=SEVERITY_COLORS,
        labels={"month": "Month", "count": "Accidents"},
    )
    st.plotly_chart(fig_sev_trend, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: REGIONAL COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

st.header("Regional Comparison")

col_r1, col_r2 = st.columns(2)

with col_r1:
    region_acc = df.groupby("region").size().reset_index(name="accidents").sort_values("accidents", ascending=True)
    fig_reg = px.bar(
        region_acc, y="region", x="accidents", orientation="h",
        title="Accidents by Region",
        color_discrete_sequence=["#3498db"],
        labels={"region": "Region", "accidents": "Accidents"},
    )
    st.plotly_chart(fig_reg, use_container_width=True)

with col_r2:
    region_fatal = df.groupby("region")["num_fatalities"].sum().reset_index().sort_values("num_fatalities", ascending=True)
    fig_fatal = px.bar(
        region_fatal, y="region", x="num_fatalities", orientation="h",
        title="Fatalities by Region",
        color_discrete_sequence=["#e74c3c"],
        labels={"region": "Region", "num_fatalities": "Fatalities"},
    )
    st.plotly_chart(fig_fatal, use_container_width=True)

# Severity-by-region heatmap
sev_region = df.groupby(["region", "severity"]).size().reset_index(name="count")
sev_pivot = sev_region.pivot(index="region", columns="severity", values="count").fillna(0)
sev_pivot = sev_pivot.reindex(columns=["Slight", "Serious", "Fatal"], fill_value=0)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=sev_pivot.values,
    x=sev_pivot.columns.tolist(),
    y=sev_pivot.index.tolist(),
    colorscale="YlOrRd",
    text=sev_pivot.values.astype(int),
    texttemplate="%{text}",
    hovertemplate="Region: %{y}<br>Severity: %{x}<br>Count: %{z}<extra></extra>",
))
fig_heatmap.update_layout(title="Severity by Region Heatmap", height=500)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Injury rate by region
region_metrics = df.groupby("region").agg(
    accidents=("accident_id", "count"),
    injuries=("num_injuries", "sum"),
    fatalities=("num_fatalities", "sum"),
).reset_index()
region_metrics["injury_rate"] = round(region_metrics["injuries"] / region_metrics["accidents"], 2)
region_metrics["fatality_rate"] = round(region_metrics["fatalities"] / region_metrics["accidents"] * 100, 2)
region_metrics = region_metrics.sort_values("injury_rate", ascending=True)

fig_inj_rate = px.bar(
    region_metrics, y="region", x="injury_rate", orientation="h",
    title="Average Injuries per Accident by Region",
    color_discrete_sequence=["#f39c12"],
    labels={"region": "Region", "injury_rate": "Injuries / Accident"},
)
st.plotly_chart(fig_inj_rate, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: CONTRIBUTING FACTORS
# ══════════════════════════════════════════════════════════════════════════════

st.header("Contributing Factors")

col_f1, col_f2 = st.columns(2)

with col_f1:
    weather_sev = df.groupby(["weather", "severity"]).size().reset_index(name="count")
    fig_weather = px.bar(
        weather_sev, x="weather", y="count", color="severity",
        title="Weather Conditions vs Severity",
        color_discrete_map=SEVERITY_COLORS,
        barmode="group",
        labels={"weather": "Weather", "count": "Accidents"},
    )
    st.plotly_chart(fig_weather, use_container_width=True)

with col_f2:
    road_sev = df.groupby(["road_type", "severity"]).size().reset_index(name="count")
    fig_road = px.bar(
        road_sev, x="road_type", y="count", color="severity",
        title="Road Type vs Severity",
        color_discrete_map=SEVERITY_COLORS,
        barmode="group",
        labels={"road_type": "Road Type", "count": "Accidents"},
    )
    st.plotly_chart(fig_road, use_container_width=True)

col_f3, col_f4 = st.columns(2)

with col_f3:
    speed_data = df.groupby("speed_limit").agg(
        accidents=("accident_id", "count"),
        fatalities=("num_fatalities", "sum"),
    ).reset_index()
    speed_data["fatality_pct"] = round(speed_data["fatalities"] / speed_data["accidents"] * 100, 2)
    fig_speed = px.bar(
        speed_data, x="speed_limit", y="accidents",
        title="Accidents by Speed Limit",
        color="fatality_pct",
        color_continuous_scale="Reds",
        labels={"speed_limit": "Speed Limit (km/h)", "accidents": "Accidents", "fatality_pct": "Fatality %"},
    )
    st.plotly_chart(fig_speed, use_container_width=True)

with col_f4:
    light_sev = df.groupby(["light_conditions", "severity"]).size().reset_index(name="count")
    fig_light = px.bar(
        light_sev, x="light_conditions", y="count", color="severity",
        title="Light Conditions vs Severity",
        color_discrete_map=SEVERITY_COLORS,
        barmode="group",
        labels={"light_conditions": "Light Condition", "count": "Accidents"},
    )
    st.plotly_chart(fig_light, use_container_width=True)

# Vehicle type analysis
vehicle_data = df.groupby("vehicle_type").agg(
    accidents=("accident_id", "count"),
    fatalities=("num_fatalities", "sum"),
    injuries=("num_injuries", "sum"),
).reset_index().sort_values("accidents", ascending=True)

fig_vehicle = px.bar(
    vehicle_data, y="vehicle_type", x="accidents", orientation="h",
    title="Accidents by Vehicle Type",
    color_discrete_sequence=["#1abc9c"],
    labels={"vehicle_type": "Vehicle Type", "accidents": "Accidents"},
)
st.plotly_chart(fig_vehicle, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: GEOSPATIAL MAPPING
# ══════════════════════════════════════════════════════════════════════════════

st.header("Accident Hotspot Map")

df_map = df[["latitude", "longitude", "severity", "region", "date", "num_casualties"]].copy()

map_tab1, map_tab2 = st.tabs(["Scatter Map", "Heatmap Style"])

with map_tab1:
    fig_scatter_map = px.scatter_map(
        df_map, lat="latitude", lon="longitude",
        color="severity",
        color_discrete_map=SEVERITY_COLORS,
        size="num_casualties",
        size_max=10,
        hover_data=["region", "date", "num_casualties"],
        title="Accident Locations by Severity",
        zoom=4,
        center={"lat": 22.5, "lon": 79.0},
        map_style="carto-positron",
        height=650,
    )
    fig_scatter_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_scatter_map, use_container_width=True)

with map_tab2:
    fig_density = px.density_map(
        df_map, lat="latitude", lon="longitude",
        z="num_casualties",
        radius=15,
        title="Accident Density Heatmap",
        zoom=4,
        center={"lat": 22.5, "lon": 79.0},
        map_style="carto-positron",
        height=650,
        color_continuous_scale="YlOrRd",
    )
    fig_density.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_density, use_container_width=True)

st.divider()

# ── Key Findings ──────────────────────────────────────────────────────────────

st.header("Key Findings Summary")

top_region = df.groupby("region").size().idxmax()
top_fatal_region = df.groupby("region")["num_fatalities"].sum().idxmax()
worst_weather = df[df["severity"] == "Fatal"].groupby("weather").size().idxmax() if len(df[df["severity"] == "Fatal"]) > 0 else "N/A"
peak_hour = df.groupby("hour").size().idxmax()
peak_day = df.groupby("day_of_week").size().idxmax()

findings = f"""
| Finding | Detail |
|---------|--------|
| Highest accident region | **{top_region}** |
| Highest fatality region | **{top_fatal_region}** |
| Peak accident hour | **{peak_hour}:00** |
| Peak accident day | **{peak_day}** |
| Worst weather for fatal accidents | **{worst_weather}** |
| Total fatality rate | **{fatality_rate}%** of all casualties |
| Data period | **{date_min}** to **{date_max}** |
| Total records analyzed | **{total_accidents:,}** |
"""
st.markdown(findings)

st.sidebar.markdown("---")
st.sidebar.caption("Data: road_accidents.csv | Snowflake: ROAD_ACCIDENTS_DB.ANALYTICS.ACCIDENTS")
