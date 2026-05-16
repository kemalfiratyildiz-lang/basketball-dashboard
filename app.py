import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Asist Top Kaybı Analizi", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 45%, #f1f5f9 100%);
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3, p {
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🏀 Asist / Top Kaybı Dashboard")

df = pd.read_csv("bsl_stats.csv")

player_col = "Player"
team_col = "Team"
minute_col = "MPG"
games_col = "GP"
assist_col = "APG"
turnover_col = "TOV"

for col in [minute_col, games_col, assist_col, turnover_col]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[player_col, team_col, minute_col, games_col, assist_col, turnover_col])

df = df[
    (df[minute_col] >= 10) &
    (df[games_col] >= 7) &
    (df[turnover_col] > 0)
].copy()

df["AST_TOV_RATIO"] = df[assist_col] / df[turnover_col]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df[assist_col],
    y=df[turnover_col],
    mode="markers+text",
    text=df[player_col],
    textposition="top center",
    textfont=dict(
        size=11,
        color="#0f172a",
        family="Arial Black"
    ),
    marker=dict(
        size=13,
        color=df["AST_TOV_RATIO"],
        colorscale="Viridis",
        showscale=True,
        opacity=0.9,
        line=dict(width=1.5, color="white"),
        colorbar=dict(title="AST/TOV")
    ),
    customdata=df[[team_col, games_col, minute_col, "AST_TOV_RATIO"]],
    hovertemplate=
        "<b>%{text}</b><br>" +
        "Takım: %{customdata[0]}<br>" +
        "Maç: %{customdata[1]}<br>" +
        "Dakika: %{customdata[2]:.1f}<br>" +
        "Asist: %{x:.1f}<br>" +
        "Top Kaybı: %{y:.1f}<br>" +
        "AST/TOV: %{customdata[3]:.2f}<extra></extra>"
))

fig.update_layout(
    title=dict(
        text="10+ Dakika & 7+ Maç: Asist vs Top Kaybı",
        x=0.5,
        font=dict(size=28, color="#0f172a")
    ),
    height=850,
    plot_bgcolor="rgba(255,255,255,0.92)",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(color="#0f172a", family="Arial"),
    xaxis=dict(
        title="Asist Ortalaması (APG)",
        gridcolor="rgba(15,23,42,0.15)",
        zeroline=False
    ),
    yaxis=dict(
        title="Top Kaybı Ortalaması (TOV)",
        gridcolor="rgba(15,23,42,0.15)",
        zeroline=False
    ),
    margin=dict(l=70, r=70, t=90, b=70)
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtrelenmiş Oyuncular")

st.dataframe(
    df[[player_col, team_col, games_col, minute_col, assist_col, turnover_col, "AST_TOV_RATIO"]]
    .sort_values("AST_TOV_RATIO", ascending=False),
    use_container_width=True
)