import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asist / Top Kaybı Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #f8fbff !important;
    color: #0f172a !important;
}

.block-container {
    padding: 2rem 2rem 2rem 2rem;
    max-width: 100%;
}

h1, h2, h3, p, label, div, span {
    color: #0f172a !important;
}

.card {
    background: white;
    border: 1px solid #dbeafe;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.08);
    margin-bottom: 18px;
}

div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #93c5fd !important;
    border-radius: 12px !important;
}

div[data-testid="stButton"] button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
}

div[data-testid="stButton"] button:hover {
    background: #dbeafe !important;
}

.selected-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 10px 14px;
    font-weight: 800;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏀 Asist / Top Kaybı Dashboard")

st.markdown("""
**10+ dakika oynayan ve en az 7 maça çıkan oyuncuların interaktif asist / top kaybı analizi.**
""")

df = pd.read_csv("bsl_stats.csv")

player_col = "Player"
team_col = "Team"
minute_col = "MPG"
games_col = "GP"
assist_col = "APG"
turnover_col = "TOV"

df[team_col] = df[team_col].replace({
    "PIN": "KAR",
    "BAHC": "BAH",
    "BURS": "BUR",
    "DEM": "BÜY",
    "ENEN": "ESE",
    "MANI": "MAN",
    "SOC": "ALI",
    "TUR": "TT"
})

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
    (df[assist_col] > 1.5) &
    (df[turnover_col] > 0)
].copy()

df["AST_TOV_RATIO"] = df[assist_col] / df[turnover_col]

teams = sorted(df[team_col].unique())
players_all = sorted(df[player_col].unique())

if "selected_team" not in st.session_state:
    st.session_state.selected_team = "Tüm Takımlar"

if "compare_players" not in st.session_state:
    st.session_state.compare_players = []

left, right = st.columns([1, 3], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏀 Takım Seç")

    team_search = st.text_input(
        "Takım ara",
        placeholder="KAR, BAH, BUR...",
        label_visibility="collapsed"
    )

    shown_teams = [t for t in teams if team_search.lower() in t.lower()]

    if st.button("Tüm Takımlar", use_container_width=True):
        st.session_state.selected_team = "Tüm Takımlar"

    team_cols = st.columns(3)

    for i, team in enumerate(shown_teams):
        with team_cols[i % 3]:
            if st.button(team, key=f"team_{team}", use_container_width=True):
                st.session_state.selected_team = team

    st.markdown(
        f'<div class="selected-box">Seçili takım: {st.session_state.selected_team}</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚔️ Oyuncu Karşılaştır")

    player_search = st.text_input(
        "Oyuncu ara",
        placeholder="Oyuncu adı yaz...",
        label_visibility="collapsed"
    )

    suggestions = [
        p for p in players_all
        if player_search.lower() in p.lower()
    ] if player_search else []

    for player in suggestions[:10]:
        if st.button(player, key=f"player_{player}", use_container_width=True):
            if player not in st.session_state.compare_players:
                if len(st.session_state.compare_players) < 8:
                    st.session_state.compare_players.append(player)
                else:
                    st.warning("En fazla 8 oyuncu seçebilirsin.")

    if st.session_state.compare_players:
        st.markdown(
            f'<div class="selected-box">Seçilenler:<br>{", ".join(st.session_state.compare_players)}</div>',
            unsafe_allow_html=True
        )

        if st.button("Seçimi Temizle", use_container_width=True):
            st.session_state.compare_players = []

    st.markdown('</div>', unsafe_allow_html=True)

selected_team = st.session_state.selected_team
compare_players = st.session_state.compare_players

if selected_team != "Tüm Takımlar":
    df = df[df[team_col] == selected_team].copy()

base_df = df[~df[player_col].isin(compare_players)].copy()
highlight_df = df[df[player_col].isin(compare_players)].copy()

with right:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=base_df[assist_col],
        y=base_df[turnover_col],
        mode="markers+text",
        text=base_df[player_col],
        textposition="top center",
        textfont=dict(size=8, color="#0f172a"),
        marker=dict(
            size=base_df[minute_col] * 1.05,
            color=base_df["AST_TOV_RATIO"],
            colorscale="Viridis",
            opacity=0.72,
            showscale=True,
            line=dict(width=1, color="white"),
            colorbar=dict(
                title=dict(text="AST/TOV", font=dict(color="#0f172a", size=13)),
                tickfont=dict(color="#0f172a", size=11),
                x=1.04,
                len=0.75
            )
        ),
        customdata=base_df[[team_col, games_col, minute_col, "AST_TOV_RATIO"]],
        hovertemplate=
            "<b>%{text}</b><br>" +
            "Takım: %{customdata[0]}<br>" +
            "Maç: %{customdata[1]}<br>" +
            "Dakika: %{customdata[2]:.1f}<br>" +
            "Asist: %{x:.1f}<br>" +
            "Top Kaybı: %{y:.1f}<br>" +
            "AST/TOV: %{customdata[3]:.2f}<extra></extra>",
        name="Oyuncular"
    ))

    if not highlight_df.empty:
        fig.add_trace(go.Scatter(
            x=highlight_df[assist_col],
            y=highlight_df[turnover_col],
            mode="markers+text",
            text=highlight_df[player_col],
            textposition="top center",
            textfont=dict(size=15, color="#dc2626"),
            marker=dict(
                size=highlight_df[minute_col] * 1.9,
                color="#ef4444",
                opacity=1,
                line=dict(width=4, color="#7f1d1d")
            ),
            customdata=highlight_df[[team_col, games_col, minute_col, "AST_TOV_RATIO"]],
            hovertemplate=
                "<b>%{text}</b><br>" +
                "Takım: %{customdata[0]}<br>" +
                "Maç: %{customdata[1]}<br>" +
                "Dakika: %{customdata[2]:.1f}<br>" +
                "Asist: %{x:.1f}<br>" +
                "Top Kaybı: %{y:.1f}<br>" +
                "AST/TOV: %{customdata[3]:.2f}<extra></extra>",
            name="Karşılaştırılan Oyuncular"
        ))

    fig.update_layout(
        title=dict(
            text="10+ Dakika & 7+ Maç: Asist vs Top Kaybı",
            x=0.5,
            font=dict(size=27, color="#0f172a")
        ),
        height=720,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#0f172a"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#0f172a", size=12)
        ),
        xaxis=dict(
            title="Asist Ortalaması (APG)",
            tickfont=dict(size=13, color="#0f172a"),
            title_font=dict(size=17, color="#0f172a"),
            gridcolor="rgba(15,23,42,0.10)",
            zeroline=False
        ),
        yaxis=dict(
            title="Top Kaybı Ortalaması (TOV)",
            tickfont=dict(size=13, color="#0f172a"),
            title_font=dict(size=17, color="#0f172a"),
            gridcolor="rgba(15,23,42,0.10)",
            zeroline=False
        ),
        margin=dict(l=70, r=105, t=90, b=70)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

if compare_players:
    st.subheader("⚔️ Oyuncu Karşılaştırma")

    compare_df = df[df[player_col].isin(compare_players)][[
        player_col,
        team_col,
        games_col,
        minute_col,
        assist_col,
        turnover_col,
        "AST_TOV_RATIO"
    ]].sort_values("AST_TOV_RATIO", ascending=False)

    compare_df = compare_df.rename(columns={
        player_col: "Oyuncu",
        team_col: "Takım",
        games_col: "Maç",
        minute_col: "Dakika",
        assist_col: "Asist",
        turnover_col: "Top Kaybı",
        "AST_TOV_RATIO": "AST/TOV"
    })

    st.dataframe(compare_df, use_container_width=True, hide_index=True)

st.subheader("📋 Oyuncu Tablosu")

table_df = df[[
    player_col,
    team_col,
    games_col,
    minute_col,
    assist_col,
    turnover_col,
    "AST_TOV_RATIO"
]].sort_values("AST_TOV_RATIO", ascending=False)

table_df = table_df.rename(columns={
    player_col: "Oyuncu",
    team_col: "Takım",
    games_col: "Maç",
    minute_col: "Dakika",
    assist_col: "Asist",
    turnover_col: "Top Kaybı",
    "AST_TOV_RATIO": "AST/TOV"
})

st.dataframe(table_df, use_container_width=True, hide_index=True)