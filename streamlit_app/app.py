import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌍 Weather Around the World Dashboard 🌍")
st.markdown("Interactive dashboard using scraped weather dataset from www.timeanddate.com/weather")


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "weather_data.csv")

# loading csv to data frame

df = pd.read_csv(file_path)
# changinf format of temperature_num for calculations

df["temperature_num"] = pd.to_numeric(df["temperature_num"], errors="coerce")
df = df.dropna(subset=["temperature_num"])


#side baar

st.sidebar.header("Filters")

# Dropdown menu for selecting a country or all countries

country_filter = st.sidebar.selectbox(
    "Select Country",
    ["All"] + sorted(df["country"].dropna().unique())
)

# Slider allowing users to choose a temperature range.

temp_range = st.sidebar.slider(
    "Temperature Range (°F)",
    int(df["temperature_num"].min()),
    int(df["temperature_num"].max()),
    (30, 100)
)

# Filtering the DataFrame based on the selected temperature range.

filtered_df = df[
    (df["temperature_num"] >= temp_range[0]) &
    (df["temperature_num"] <= temp_range[1])
]
# Filtering country as per users selection

if country_filter != "All":
    filtered_df = filtered_df[filtered_df["country"] == country_filter]
 
# Creating three columns to display summary statistics side-by-side.   

col1, col2, col3 = st.columns(3)

# showing city count, average temp and max temp

col1.metric("Cities", len(filtered_df))
col2.metric("Avg Temp (°F)", round(filtered_df["temperature_num"].mean(), 1))
col3.metric("Max Temp (°F)", filtered_df["temperature_num"].max())

st.divider()

# Display the filtered weather data in a table.
st.subheader("📊 Weather Data")
table_df = filtered_df.drop(columns=["image", "temperature_num"], errors="ignore")
st.dataframe(table_df, use_container_width=True)

# chart 1 bar

st.subheader("🌡️ Temperature by City")

fig1 = px.bar(
    filtered_df,
    x="city",
    y="temperature_num",
    color="temperature_num",
    title="Temperature Comparison"
)

st.plotly_chart(fig1, use_container_width=True)

# chart temperature grouping of cities

st.subheader("📈 Temperature Distribution")

fig2 = px.histogram(
    filtered_df,
    x="temperature_num",
    nbins=15,
    title="Temperature Distribution"
)

st.plotly_chart(fig2, use_container_width=True)


# chart 3 wearher types 

st.subheader("☁️ Weather Conditions")

weather_counts = filtered_df["weather"].value_counts().reset_index()
weather_counts.columns = ["weather", "count"]

fig3 = px.pie(
    weather_counts,
    names="weather",
    values="count",
    title="Weather Breakdown"
)

st.plotly_chart(fig3, use_container_width=True)



# chart 4 avgerage temp of country 

st.subheader("🌍 Average Temperature by Country")

country_temp = (
    filtered_df.groupby("country")["temperature_num"]
    .mean()
    .reset_index()
    .sort_values("temperature_num", ascending=False)
)

fig4 = px.bar(
    country_temp,
    x="country",
    y="temperature_num",
    color="temperature_num",
    title="Average Temperature by Country",
    labels={
        "country": "Country",
        "temperature_num": "Average Temperature (°F)"
    }
)

st.plotly_chart(fig4, use_container_width=True)