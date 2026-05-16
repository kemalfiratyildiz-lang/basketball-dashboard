import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asist / Top Kaybı Dashboard",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #f8fbff 0%, #dbeafe 55%, #f1f5f9 100%);
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 100%;
}

h1, h2, h3, p, label, div {
    font-family: 'Inter', sans-serif !important;
    color: #0f172a;
}

h1 {
    font-weight: 900 !important;
    font-size: 3rem !important;
}

.chart-card {
    background: rgba(255,255,255,0.58);
    border-radius: 20px;
    padding: 28px 28px 8px 28px;
    margin-top: 20px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}

[data-testid="stSelectbox"] {
    max-width: 520px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏀 Asist / Top Kaybı Dashboard")

st.markdown("""
**10+ dakika oynayan ve en az 7 maça çıkan oyuncuların  
interaktif asist / top kaybı analizi.**
""")

df = pd.read_csv("bsl_stats.csv")

player_col = "Player"
team_col = "Team"
minute_col = "MPG"
games_col = "GP"
assist_col = "APG"
turnover_col = "TOV"

teams = sorted(df[team_col].dropna().unique())

selected_team = st.selectbox(
    "Takım Seç",
    ["Tüm Takımlar"] + teams
)

if selected_team != "Tüm Takımlar":
    df = df[df[team_col] == selected_team].copy()

for col in [minute_col, games_col, assist_col, turnover_col]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[
    player_col,
    team_col,
    minute_col,
    games_col,
    assist_col,
    turnover_col
])

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
        size=10,
        color="#0f172a",
        family="Inter, Arial, sans-serif"
    ),
    marker=dict(
        size=df[minute_col] * 1.15,
        color=df["AST_TOV_RATIO"],
        colorscale="Viridis",
        showscale=True,
        opacity=0.90,
        line=dict(
            width=1.4,
            color="white"
        ),
        colorbar=dict(
            title=dict(
                text="AST/TOV",
                font=dict(
                    size=14,
                    color="#0f172a",
                    family="Inter, Arial, sans-serif"
                )
            ),
            tickfont=dict(
                size=13,
                color="#0f172a",
                family="Inter, Arial, sans-serif"
            )
        )
    ),
    customdata=df[[
        team_col,
        games_col,
        minute_col,
        "AST_TOV_RATIO"
    ]],
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
        font=dict(
            size=34,
            color="#0f172a",
            family="Inter, Arial, sans-serif"
        )
    ),
    height=760,
    plot_bgcolor="#ffffff",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(
        color="#0f172a",
        family="Inter, Arial, sans-serif"
    ),
    xaxis=dict(
        title="Asist Ortalaması (APG)",
        gridcolor="rgba(15,23,42,0.10)",
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor="#111827",
        tickfont=dict(
            size=18,
            color="#0f172a",
            family="Inter, Arial, sans-serif"
        ),
        title_font=dict(
            size=22,
            color="#0f172a",
            family="Inter, Arial, sans-serif"
        )
    ),
    yaxis=dict(
        title="Top Kaybı Ortalaması (TOV)",
        gridcolor="rgba(15,23,42,0.10)",
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor="#111827",
        tickfont=dict(
            size=18,
            color="#0f172a",
            family="Inter, Arial, sans-serif"
        ),
        title_font=dict(
            size=22,
            color="#0f172a",
            family="Inter, Arial, sans-serif"
        )
    ),
    margin=dict(
        l=130,
        r=90,
        t=110,
        b=90
    )
)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Oyuncu Tablosu")

table_df = df[[
    player_col,
    team_col,
    games_col,
    minute_col,
    assist_col,
    turnover_col,
    "AST_TOV_RATIO"
]].sort_values(
    "AST_TOV_RATIO",
    ascending=False
)

st.dataframe(
    table_df,
    use_container_width=True
)