import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="BSL TS Dashboard",
    layout="wide"
)

FONT = "Arial, Helvetica, sans-serif"
BOLD_FONT = "Arial Black, Arial, Helvetica, sans-serif"

df = pd.read_csv("bsl_stats.csv")
df.columns = df.columns.str.strip()

team_replace = {
    "BAHC": "BAH",
    "BURS": "BUR",
    "DEM": "BÜY",
    "ENEN": "ESE",
    "MANI": "MAN",
    "SOC": "ALI",
    "TUR": "TT",
    "PIN": "KSK"
}

df["Team"] = df["Team"].replace(team_replace)

numeric_cols = [
    "GP", "MPG", "PPG", "FGM", "FGA", "FG%",
    "3PM", "3PA", "3P%", "FTM", "FTA", "FT%",
    "RPG", "APG", "TOV"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["FG%", "3P%", "FT%"]:
    if col in df.columns:
        df[col] = df[col].apply(
            lambda x: x / 10 if pd.notna(x) and x > 100 else x
        )

df["TS%"] = (
    df["PPG"] /
    (2 * (df["FGA"] + 0.44 * df["FTA"]))
) * 100

df = df.dropna(subset=[
    "Player", "Team", "GP", "MPG",
    "PPG", "FGA", "FTA", "TS%"
])

df = df[df["FGA"] > 0].copy()

df_all_players = df.copy()

df_main_filtered = df[
    (df["GP"] >= 8) &
    (df["PPG"] >= 8)
].copy()

st.markdown("""
<style>
* {
    font-family: Arial, Helvetica, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 190, 95, 0.22), transparent 34%),
        radial-gradient(circle at bottom right, rgba(126, 87, 194, 0.22), transparent 34%),
        linear-gradient(135deg, #070504 0%, #17110c 48%, #050505 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

h1, h2, h3, p, label, div, span {
    color: #f7ead2 !important;
}

h1, h2, h3,
.card-title,
.selected-pill,
.suggestion-title {
    font-family: Arial Black, Arial, Helvetica, sans-serif !important;
}

h1 {
    font-size: 2.35rem !important;
    font-weight: 900 !important;
    letter-spacing: -1.4px;
    color: #f6d58a !important;
}

.info-card {
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255, 218, 158, 0.20);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 24px 60px rgba(0,0,0,0.36);
    backdrop-filter: blur(12px);
}

.card-title {
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 12px;
    color: #ffd47a !important;
}

.selected-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(255, 207, 99, 0.16);
    border: 1px solid rgba(255, 207, 99, 0.32);
    color: #ffcf63 !important;
    font-weight: 900;
    line-height: 1.5;
}

.suggestion-title {
    font-weight: 900;
    margin-top: 14px;
    margin-bottom: 8px;
    color: #dbc6a0 !important;
}

.chart-card {
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255, 218, 158, 0.22);
    border-radius: 30px;
    padding: 16px;
    box-shadow: 0 30px 85px rgba(0,0,0,0.42);
    overflow: hidden;
    backdrop-filter: blur(12px);
}

div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.10) !important;
    color: #f7ead2 !important;
    border: 1px solid rgba(255, 218, 158, 0.30) !important;
    border-radius: 15px !important;
    min-height: 46px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #a99b83 !important;
    opacity: 1 !important;
}

div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.10) !important;
    color: #f7ead2 !important;
    border: 1px solid rgba(255, 218, 158, 0.26) !important;
    border-radius: 999px !important;
    padding: 8px 13px !important;
    font-weight: 900 !important;
    width: 100%;
}

div[data-testid="stButton"] button:hover {
    background: rgba(255, 207, 99, 0.18) !important;
    color: #ffcf63 !important;
}

div[data-testid="stCheckbox"] label {
    font-weight: 900 !important;
}

div[data-testid="stRadio"] label {
    color: #f7ead2 !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
}
</style>
""", unsafe_allow_html=True)

if "highlight_players" not in st.session_state:
    st.session_state.highlight_players = []

if "compare_players" not in st.session_state:
    st.session_state.compare_players = []

if "only_compare_graph" not in st.session_state:
    st.session_state.only_compare_graph = False

st.title("🏀 BSL Sayı & True Shooting Dashboard")

left, right = st.columns([1.05, 4.35])

with left:
    teams = sorted(df_all_players["Team"].dropna().unique())

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏀 Takım Filtrele</div>', unsafe_allow_html=True)

    team_search = st.text_input(
        "Takım ara",
        placeholder="Takım kodu yaz...",
        label_visibility="collapsed"
    )

    filtered_teams = [
        team for team in teams
        if team_search.lower() in team.lower()
    ]

    selected_team = st.radio(
        "",
        ["Tüm Takımlar"] + filtered_teams,
        label_visibility="collapsed"
    )

    st.markdown(
        f'<div class="selected-pill">Seçili takım: {selected_team}</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if selected_team == "Tüm Takımlar":
        active_df = df_main_filtered.copy()
    else:
        active_df = df_all_players[df_all_players["Team"] == selected_team].copy()

    players = sorted(active_df["Player"].dropna().unique())

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👤 Oyuncu Bul / Vurgula</div>', unsafe_allow_html=True)

    player_search = st.text_input(
        "Oyuncu ara",
        placeholder="Oyuncu adını yaz...",
        label_visibility="collapsed"
    )

    player_suggestions = [
        player for player in players
        if player_search.lower() in player.lower()
    ] if player_search else []

    if player_suggestions:
        st.markdown('<div class="suggestion-title">Öneriler</div>', unsafe_allow_html=True)

        for player in player_suggestions[:8]:
            if st.button(player, key=f"highlight_{player}"):
                if player not in st.session_state.highlight_players:
                    st.session_state.highlight_players.append(player)

    if st.session_state.highlight_players:
        st.markdown(
            f'<div class="selected-pill">Vurgulanan: {", ".join(st.session_state.highlight_players)}</div>',
            unsafe_allow_html=True
        )

        if st.button("Vurgulamayı temizle"):
            st.session_state.highlight_players = []

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚔️ Oyuncu Karşılaştır</div>', unsafe_allow_html=True)

    compare_search = st.text_input(
        "Karşılaştırma arama",
        placeholder="Oyuncu adı yaz...",
        label_visibility="collapsed"
    )

    compare_suggestions = [
        player for player in players
        if compare_search.lower() in player.lower()
    ] if compare_search else []

    if compare_suggestions:
        st.markdown('<div class="suggestion-title">Öneriler</div>', unsafe_allow_html=True)

        for player in compare_suggestions[:8]:
            if st.button(player, key=f"compare_{player}"):
                if player not in st.session_state.compare_players:
                    if len(st.session_state.compare_players) < 6:
                        st.session_state.compare_players.append(player)
                    else:
                        st.warning("En fazla 6 oyuncu seçebilirsin.")

    if st.session_state.compare_players:
        st.markdown(
            f'<div class="selected-pill">Karşılaştırılan: {", ".join(st.session_state.compare_players)}</div>',
            unsafe_allow_html=True
        )

        st.session_state.only_compare_graph = st.checkbox(
            "Grafikte sadece karşılaştırılan oyuncular kalsın",
            value=st.session_state.only_compare_graph
        )

        if st.button("Karşılaştırmayı temizle"):
            st.session_state.compare_players = []
            st.session_state.only_compare_graph = False

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    selected_graph_players = list(
        dict.fromkeys(st.session_state.highlight_players + st.session_state.compare_players)
    )

    active_df["IS_HIGHLIGHTED"] = active_df["Player"].isin(selected_graph_players)

    if st.session_state.only_compare_graph and st.session_state.compare_players:
        graph_df = active_df[active_df["Player"].isin(st.session_state.compare_players)].copy()
    else:
        graph_df = active_df.copy()

    graph_df["IS_HIGHLIGHTED"] = graph_df["Player"].isin(selected_graph_players)

    base_df = graph_df[~graph_df["IS_HIGHLIGHTED"]].copy()
    highlight_df = graph_df[graph_df["IS_HIGHLIGHTED"]].copy()

    fig = go.Figure()

    if not base_df.empty:
        fig.add_trace(go.Scatter(
            x=base_df["PPG"],
            y=base_df["TS%"],
            mode="markers+text",
            text=base_df["Player"],
            textposition="top center",
            textfont=dict(size=8, color="rgba(247,234,210,0.70)", family=FONT),
            marker=dict(
                size=base_df["MPG"] * 1.05,
                color=base_df["TS%"],
                colorscale=[
                    [0.0, "#5b4b8a"],
                    [0.35, "#8b7cff"],
                    [0.65, "#f0b35a"],
                    [1.0, "#ffcf63"]
                ],
                showscale=True,
                opacity=0.84,
                line=dict(width=1.2, color="rgba(255,255,255,0.72)"),
                colorbar=dict(
                    title=dict(text="TS%", font=dict(size=15, color="#f7ead2", family=BOLD_FONT)),
                    tickfont=dict(size=13, color="#f7ead2", family=FONT),
                    outlinewidth=0,
                    thickness=25,
                    len=0.78
                )
            ),
            customdata=base_df[[
                "Team", "GP", "MPG", "FGA", "FTA", "FG%", "3P%", "FT%"
            ]],
            hovertemplate=
                "<b>%{text}</b><br>" +
                "Takım: %{customdata[0]}<br>" +
                "Maç: %{customdata[1]:.0f}<br>" +
                "Dakika: %{customdata[2]:.1f}<br>" +
                "PPG: %{x:.1f}<br>" +
                "TS%: %{y:.1f}<br>" +
                "FGA: %{customdata[3]:.1f}<br>" +
                "FTA: %{customdata[4]:.1f}<br>" +
                "FG%: %{customdata[5]:.1f}%<br>" +
                "3P%: %{customdata[6]:.1f}%<br>" +
                "FT%: %{customdata[7]:.1f}%<extra></extra>",
            showlegend=False
        ))

    if not highlight_df.empty:
        fig.add_trace(go.Scatter(
            x=highlight_df["PPG"],
            y=highlight_df["TS%"],
            mode="markers+text",
            text=highlight_df["Player"],
            textposition="top center",
            textfont=dict(size=13, color="#ffcf63", family=BOLD_FONT),
            marker=dict(
                size=highlight_df["MPG"] * 1.7,
                color="#ffcf63",
                opacity=0.98,
                line=dict(width=4, color="#fff1bf")
            ),
            customdata=highlight_df[[
                "Team", "GP", "MPG", "FGA", "FTA", "FG%", "3P%", "FT%"
            ]],
            hovertemplate=
                "<b>%{text}</b><br>" +
                "Takım: %{customdata[0]}<br>" +
                "Maç: %{customdata[1]:.0f}<br>" +
                "Dakika: %{customdata[2]:.1f}<br>" +
                "PPG: %{x:.1f}<br>" +
                "TS%: %{y:.1f}<br>" +
                "FGA: %{customdata[3]:.1f}<br>" +
                "FTA: %{customdata[4]:.1f}<br>" +
                "FG%: %{customdata[5]:.1f}%<br>" +
                "3P%: %{customdata[6]:.1f}%<br>" +
                "FT%: %{customdata[7]:.1f}%<extra></extra>",
            showlegend=False
        ))

    if selected_team == "Tüm Takımlar":
        chart_title = "MIN. 8 MAÇ & 8 SAYI: PPG vs TRUE SHOOTING %"
    else:
        chart_title = f"{selected_team}: TÜM OYUNCULAR — PPG vs TRUE SHOOTING %"

    fig.update_layout(
        title=dict(
            text=chart_title,
            x=0.5,
            y=0.965,
            font=dict(size=22, color="#f6d58a", family=BOLD_FONT)
        ),
        height=760,
        plot_bgcolor="rgba(255,255,255,0.035)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f7ead2", family=FONT),
        showlegend=False,
        xaxis=dict(
            title=dict(
                text="Sayı Ortalaması (PPG)",
                font=dict(size=20, color="#f7ead2", family=BOLD_FONT)
            ),
            tickfont=dict(size=16, color="#f7ead2", family=BOLD_FONT),
            gridcolor="rgba(255,255,255,0.10)",
            gridwidth=1,
            zeroline=False,
            linecolor="rgba(255,255,255,0.42)",
            linewidth=2,
            mirror=True,
            automargin=True
        ),
        yaxis=dict(
            title=dict(
                text="True Shooting % (TS%)",
                font=dict(size=20, color="#f7ead2", family=BOLD_FONT)
            ),
            tickfont=dict(size=16, color="#f7ead2", family=BOLD_FONT),
            gridcolor="rgba(255,255,255,0.10)",
            gridwidth=1,
            zeroline=False,
            linecolor="rgba(255,255,255,0.42)",
            linewidth=2,
            mirror=True,
            automargin=True
        ),
        margin=dict(l=110, r=130, t=100, b=90)
    )

    fig.update_xaxes(
        showgrid=True,
        minor=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.045)"
        )
    )

    fig.update_yaxes(
        showgrid=True,
        minor=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.045)"
        )
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.compare_players:
        st.subheader("⚔️ Oyuncu Karşılaştırma")

        compare_df = active_df[active_df["Player"].isin(st.session_state.compare_players)][[
            "Player", "Team", "GP", "MPG", "PPG", "TS%",
            "FGA", "FTA", "FG%", "3P%", "FT%"
        ]].sort_values("PPG", ascending=False)

        for col in ["PPG", "MPG", "TS%", "FG%", "3P%", "FT%", "FGA", "FTA"]:
            compare_df[col] = compare_df[col].round(1)

        st.dataframe(
            compare_df,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Oyuncu Tablosu")

    table_df = active_df[[
        "Player", "Team", "GP", "MPG", "PPG", "TS%",
        "FGA", "FTA", "FG%", "3P%", "FT%"
    ]].sort_values(["PPG", "TS%"], ascending=False)

    for col in ["PPG", "MPG", "TS%", "FG%", "3P%", "FT%", "FGA", "FTA"]:
        table_df[col] = table_df[col].round(1)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )