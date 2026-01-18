import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px

# Set page config
st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

# Title
st.title(" Washington D.C. Bike Rental Dashboard")
st.markdown("Interactive exploration of bike rental trends (2011–2012)")

# Load dataset (assuming it's in the same folder)
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv", parse_dates=["datetime"])
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["day_of_week"] = df["datetime"].dt.day_name()
    df["hour"] = df["datetime"].dt.hour
    df["day_period"] = pd.cut(df["hour"], 
                               bins=[0, 6, 12, 18, 24], 
                               labels=["Night", "Morning", "Afternoon", "Evening"], 
                               right=False)
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    df["season"] = df["season"].map(season_map)
    return df

df = load_data()

# Sidebar for interactive widgets
st.sidebar.header("🔧 Controls")

# Widget 1: Year selection
selected_year = st.sidebar.selectbox("Select Year", options=[2011, 2012, "Both"], index=2)

# Widget 2: Season selection
selected_season = st.sidebar.multiselect(
    "Select Season(s)", 
    options=["Spring", "Summer", "Fall", "Winter"], 
    default=["Spring", "Summer", "Fall", "Winter"]
)

# Widget 3: Day type selection
day_type = st.sidebar.radio("Day Type", options=["All", "Working Day", "Holiday/Weekend"])

# Filter data based on widgets
filtered_df = df.copy()
if selected_year != "Both":
    filtered_df = filtered_df[filtered_df["year"] == selected_year]
if selected_season:
    filtered_df = filtered_df[filtered_df["season"].isin(selected_season)]
if day_type == "Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif day_type == "Holiday/Weekend":
    filtered_df = filtered_df[filtered_df["workingday"] == 0]

# Display filtered dataset info
st.sidebar.write(f" Filtered Rows: **{len(filtered_df)}**")

# Main Dashboard
st.header("📈 Visualizations")

# Row 1: Two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Rentals by Hour of Day")
    hourly_avg = filtered_df.groupby("hour")["count"].mean()
    fig1, ax1 = plt.subplots()
    ax1.plot(hourly_avg.index, hourly_avg.values, marker="o", color="teal")
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Average Rentals")
    ax1.grid(True)
    st.pyplot(fig1)

with col2:
    st.subheader("2. Rentals by Season")
    season_avg = filtered_df.groupby("season")["count"].mean()
    fig2, ax2 = plt.subplots()
    ax2.bar(season_avg.index, season_avg.values, color="skyblue")
    ax2.set_ylabel("Average Rentals")
    st.pyplot(fig2)

# Row 2
st.subheader("3. Rentals by Weather Condition")
weather_avg = filtered_df.groupby("weather")["count"].mean()
fig3, ax3 = plt.subplots()
ax3.bar(weather_avg.index.astype(str), weather_avg.values, color="orange")
ax3.set_xlabel("Weather (1=Clear, 4=Heavy Rain/Snow)")
ax3.set_ylabel("Average Rentals")
st.pyplot(fig3)

# Row 3
st.subheader("4. Rentals by Day Period")
period_avg = filtered_df.groupby("day_period")["count"].mean()
fig4, ax4 = plt.subplots()
ax4.bar(period_avg.index, period_avg.values, color="green")
ax4.set_ylabel("Average Rentals")
st.pyplot(fig4)

# Row 4: Heatmap (correlation matrix)
st.subheader("5. Correlation Heatmap")
numerical_cols = ["temp", "atemp", "humidity", "windspeed", "casual", "registered", "count"]
corr = filtered_df[numerical_cols].corr()
fig5, ax5 = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax5)
st.pyplot(fig5)

# Row 5: Interactive Plotly plot
st.subheader("6. Interactive Scatter: Temp vs. Rentals")
fig6 = px.scatter(filtered_df, x="temp", y="count", color="season", 
                  hover_data=["humidity", "windspeed"])
st.plotly_chart(fig6, use_container_width=True)

# Summary Stats
st.header("Summary Statistics")
st.dataframe(filtered_df[["count", "casual", "registered", "temp", "humidity"]].describe())

# Footer
st.markdown("---")

st.markdown("*Dashboard created with Streamlit | Data from Kaggle*")
