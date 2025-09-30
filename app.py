import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Football Player Performance Analytics", layout="wide")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("players_list.csv")
    if "Unnamed: 0" in df.columns:
        df.drop(columns="Unnamed: 0", inplace=True)
    return df

df = load_data()

st.title("⚽ Football Player Performance Analytics")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

# Team filter
teams = sorted(df["Team"].dropna().unique())
selected_teams = st.sidebar.multiselect("Select National Team(s)", teams)

# Position filter
positions = sorted(df["Pos"].dropna().unique())
selected_positions = st.sidebar.multiselect("Select Position(s)", positions)

# Age range
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

# ---------- APPLY FILTERS ----------
filtered = df.copy()
if selected_teams:
    filtered = filtered[filtered["Team"].isin(selected_teams)]
if selected_positions:
    filtered = filtered[filtered["Pos"].isin(selected_positions)]
filtered = filtered[(filtered["Age"] >= age_range[0]) & (filtered["Age"] <= age_range[1])]

if filtered.empty:
    st.warning("No players match the selected filters.")
    st.stop()

# ---------- CALCULATE METRICS ----------
filtered["PassingAccuracy"] = filtered["pass_comp%"].fillna(
    (filtered["pass_comp"] / filtered["pass_attempt"] * 100)
)
filtered["Goals_per90"] = filtered["Gls"] / (filtered["Minutes_played"] / 90)
filtered["Assists_per90"] = filtered["Ast"] / (filtered["Minutes_played"] / 90)
filtered["PerformanceScore"] = (
    0.4 * filtered["Goals_per90"]
    + 0.3 * filtered["Assists_per90"]
    + 0.3 * (filtered["PassingAccuracy"] / 100)
)

# ---------- SHOW PLAYER STATS TABLE ----------
st.subheader("📊 Player Statistics")
st.dataframe(
    filtered[[
        "Player","Team","Pos","Age",
        "Gls","Ast","PassingAccuracy","Goals_per90","Assists_per90"
    ]].round(2),
    use_container_width=True
)

# ---------- VISUALIZATIONS ----------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top 10 Goals")
    top_goals = filtered.nlargest(10, "Gls")
    fig, ax = plt.subplots(figsize=(6,4))
    ax.barh(top_goals["Player"], top_goals["Gls"], color="steelblue")
    ax.invert_yaxis()
    ax.set_xlabel("Goals")
    st.pyplot(fig)

with col2:
    st.markdown("### Top 10 Assists")
    top_assists = filtered.nlargest(10, "Ast")
    fig, ax = plt.subplots(figsize=(6,4))
    ax.barh(top_assists["Player"], top_assists["Ast"], color="darkorange")
    ax.invert_yaxis()
    ax.set_xlabel("Assists")
    st.pyplot(fig)

st.markdown("### Passing Accuracy Distribution")
fig, ax = plt.subplots(figsize=(8,4))
filtered["PassingAccuracy"].hist(bins=20, ax=ax, color="green", edgecolor="black")
ax.set_xlabel("Passing Accuracy (%)")
ax.set_ylabel("Number of Players")
st.pyplot(fig)

# ---------- PERFORMANCE RANKING ----------
st.subheader("🏆 Performance Ranking")
ranking = filtered.sort_values("PerformanceScore", ascending=False)
st.dataframe(
    ranking[[
        "Player","Team","Pos","Age",
        "Goals_per90","Assists_per90","PassingAccuracy","PerformanceScore"
    ]].round(2),
    use_container_width=True
)

fig, ax = plt.subplots(figsize=(8,4))
ranking.head(10).plot.bar(
    x="Player", y="PerformanceScore", ax=ax, color="purple", legend=False
)
ax.set_ylabel("Performance Score")
ax.set_title("Top 10 Players by Performance Score")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)
