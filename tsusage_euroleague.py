import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="EuroLeague Usage vs Efficiency Dashboard",
    layout="wide"
)

FONT = "Arial, Helvetica, sans-serif"
BOLD_FONT = "Arial Black, Arial, Helvetica, sans-serif"

# DATA
df = pd.read_csv("euroleague_merged_dashboard_data.csv")
df.columns = df.columns.str.strip()

df["Player"] = df["Player"].astype(str).str.strip()
df["Team"] = df["Team"].astype(str).str.strip()

# LYV -> ASV
df.loc[df["Team"] == "LYV", "Team"] = "ASV"

# PAR içindeki Paris oyuncularını PARI yap
paris_players = [
    "NADIR HIFI",
    "JUSTIN ROBINSON",
    "JARED RHODEN",
    "LAMAR STEVENS",
    "AMATH MBAYE",
    "AMATH M'BAYE",
    "SEBASTIAN HERRERA",
    "ALLAN JULIAN DOKOSSI",
    "ALLAN JULIEN DOKOSSI",
    "DAULTON HOMMES",
    "MOUHAMED FAYE",
    "MOUHAMMAD FAYE",
    "JOEL AYAYI",
    "DEREK WILLIS",
    "JEREMY MORGAN",
    "ENZO ANDRE SHAHRVIN",
    "LEOPOLD CAVALIERE",
    "YAKUBA OUATTARA",
]

df["_PLAYER_FIX"] = (
    df["Player"]
    .astype(str)
    .str.upper()
    .str.replace("’", "'", regex=False)
    .str.replace(".", "", regex=False)
    .str.strip()
)

paris_players_fixed = [
    player.replace(".", "").strip()
    for player in paris_players
]

df.loc[
    (df["Team"] == "PAR") &
    (df["_PLAYER_FIX"].isin(paris_players_fixed)),
    "Team"
] = "PARI"

df.drop(columns=["_PLAYER_FIX"], inplace=True)

# NUMERIC COLUMNS
numeric_cols = [
    "GP", "MPG", "PPG", "TS%", "eFG%", "AST%", "TOV%", "STL%", "BLK%",
    "USG%", "PPR", "PPS", "ORtg", "DRtg", "eDiff", "FIC", "PER",
    "FGM", "FGA", "FG%", "3PM", "3PA", "3P%",
    "FTM", "FTA", "FT%", "RPG", "APG", "SPG", "BPG"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# FIX PERCENTAGES
for col in ["TS%", "eFG%", "AST%", "TOV%", "USG%", "FG%", "3P%", "FT%"]:
    if col in df.columns:
        df[col] = df[col].apply(
            lambda x: x / 10 if pd.notna(x) and x > 100 else x
        )

required_cols = [
    "Player", "Team", "GP", "MPG", "PPG",
    "TS%", "USG%", "AST%", "TOV%", "ORtg", "DRtg", "PER"
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Eksik kolon var: {missing_cols}")
    st.stop()

df = df.dropna(subset=required_cols).copy()

df = df[
    (df["USG%"] > 0) &
    (df["TS%"] > 0) &
    (df["PER"] > 0)
].copy()

df_all_players = df.copy()

# CSS
st.markdown("""
<style>

* {
    font-family: Arial, Helvetica, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(80,120,255,0.20), transparent 34%),
        radial-gradient(circle at bottom right, rgba(255,80,120,0.18), transparent 34%),
        linear-gradient(135deg, #040711 0%, #101827 50%, #050505 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

h1, h2, h3, p, label, div, span {
    color: #eef3ff !important;
}

h1, h2, h3, .card-title, .selected-pill, .suggestion-title {
    font-family: Arial Black, Arial, Helvetica, sans-serif !important;
}

h1 {
    font-size: 2.35rem !important;
    font-weight: 900 !important;
    letter-spacing: -1.4px;
    color: #dce8ff !important;
}

.info-card {
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(210,225,255,0.20);
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
    color: #9fc3ff !important;
}

.selected-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(130,170,255,0.16);
    border: 1px solid rgba(130,170,255,0.32);
    color: #bcd4ff !important;
    font-weight: 900;
    line-height: 1.5;
}

.suggestion-title {
    font-weight: 900;
    margin-top: 14px;
    margin-bottom: 8px;
    color: #c8d7f4 !important;
}

.chart-card {
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(210,225,255,0.22);
    border-radius: 30px;
    padding: 16px;
    box-shadow: 0 30px 85px rgba(0,0,0,0.42);
    overflow: hidden;
    backdrop-filter: blur(12px);
}

div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.10) !important;
    color: #eef3ff !important;
    border: 1px solid rgba(210,225,255,0.30) !important;
    border-radius: 15px !important;
    min-height: 46px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #9ba9c5 !important;
    opacity: 1 !important;
}

div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.10) !important;
    color: #eef3ff !important;
    border: 1px solid rgba(210,225,255,0.26) !important;
    border-radius: 999px !important;
    padding: 8px 13px !important;
    font-weight: 900 !important;
    width: 100%;
}

div[data-testid="stButton"] button:hover {
    background: rgba(130,170,255,0.18) !important;
    color: #bcd4ff !important;
}

div[data-testid="stCheckbox"] label {
    font-weight: 900 !important;
}

div[data-testid="stRadio"] label {
    color: #eef3ff !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
}

</style>
""", unsafe_allow_html=True)

# SESSION
if "highlight_players" not in st.session_state:
    st.session_state.highlight_players = []

if "compare_players" not in st.session_state:
    st.session_state.compare_players = []

if "only_compare_graph" not in st.session_state:
    st.session_state.only_compare_graph = False

# TITLE
st.title("🏀 EuroLeague Usage vs Efficiency Dashboard")

left, right = st.columns([1.05, 4.35])

# SIDEBAR
with left:

    teams = sorted(df_all_players["Team"].dropna().unique())

    st.markdown('<div class="info-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">🏀 Takım Filtrele</div>',
        unsafe_allow_html=True
    )

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

    # FILTER
    if selected_team == "Tüm Takımlar":

        active_df = df_all_players[
            (df_all_players["GP"] >= 8) &
            (df_all_players["PPG"] >= 8)
        ].copy()

    else:

        active_df = df_all_players[
            df_all_players["Team"] == selected_team
        ].copy()

    players = sorted(active_df["Player"].dropna().unique())

    # HIGHLIGHT
    st.markdown('<div class="info-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">👤 Oyuncu Bul / Vurgula</div>',
        unsafe_allow_html=True
    )

    player_search = st.text_input(
        "Oyuncu ara",
        placeholder="Oyuncu adı yaz...",
        label_visibility="collapsed"
    )

    player_suggestions = [
        player for player in players
        if player_search.lower() in player.lower()
    ] if player_search else []

    if player_suggestions:

        st.markdown(
            '<div class="suggestion-title">Öneriler</div>',
            unsafe_allow_html=True
        )

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

    # COMPARE
    st.markdown('<div class="info-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">⚔️ Oyuncu Karşılaştır</div>',
        unsafe_allow_html=True
    )

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

        st.markdown(
            '<div class="suggestion-title">Öneriler</div>',
            unsafe_allow_html=True
        )

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

# GRAPH
with right:

    selected_graph_players = list(
        dict.fromkeys(
            st.session_state.highlight_players +
            st.session_state.compare_players
        )
    )

    active_df["IS_HIGHLIGHTED"] = active_df["Player"].isin(
        selected_graph_players
    )

    if (
        st.session_state.only_compare_graph and
        st.session_state.compare_players
    ):

        graph_df = active_df[
            active_df["Player"].isin(
                st.session_state.compare_players
            )
        ].copy()

    else:

        graph_df = active_df.copy()

    graph_df["IS_HIGHLIGHTED"] = graph_df["Player"].isin(
        selected_graph_players
    )

    base_df = graph_df[~graph_df["IS_HIGHLIGHTED"]].copy()
    highlight_df = graph_df[graph_df["IS_HIGHLIGHTED"]].copy()

    fig = go.Figure()

    # BASE PLAYERS
    if not base_df.empty:

        fig.add_trace(go.Scatter(
            x=base_df["USG%"],
            y=base_df["TS%"],
            mode="markers+text",
            text=base_df["Player"],
            textposition="top center",

            textfont=dict(
                size=8,
                color="rgba(238,243,255,0.68)",
                family=FONT
            ),

            marker=dict(
                size=base_df["PER"].clip(lower=5, upper=35) * 0.95,

                color=base_df["AST%"],

                colorscale=[
                    [0.0, "#394867"],
                    [0.35, "#5f7adb"],
                    [0.65, "#d85f8c"],
                    [1.0, "#ffb3c7"]
                ],

                showscale=True,

                opacity=0.82,

                line=dict(
                    width=1,
                    color="rgba(255,255,255,0.55)"
                ),

                colorbar=dict(
                    title=dict(
                        text="AST%",
                        font=dict(
                            size=15,
                            color="#eef3ff",
                            family=BOLD_FONT
                        )
                    ),

                    tickfont=dict(
                        size=13,
                        color="#eef3ff",
                        family=FONT
                    ),

                    outlinewidth=0,
                    thickness=25,
                    len=0.78
                )
            ),

            customdata=base_df[[
                "Team", "GP", "MPG", "PPG",
                "PER", "AST%", "TOV%",
                "ORtg", "DRtg"
            ]],

            hovertemplate=
                "<b>%{text}</b><br>" +
                "Takım: %{customdata[0]}<br>" +
                "Maç: %{customdata[1]:.0f}<br>" +
                "Dakika: %{customdata[2]:.1f}<br>" +
                "Sayı: %{customdata[3]:.1f}<br>" +
                "USG%: %{x:.1f}<br>" +
                "TS%: %{y:.1f}<br>" +
                "PER: %{customdata[4]:.1f}<br>" +
                "AST%: %{customdata[5]:.1f}<br>" +
                "TOV%: %{customdata[6]:.1f}<br>" +
                "ORtg: %{customdata[7]:.1f}<br>" +
                "DRtg: %{customdata[8]:.1f}<extra></extra>",

            showlegend=False
        ))

    # HIGHLIGHT PLAYERS
    if not highlight_df.empty:

        fig.add_trace(go.Scatter(
            x=highlight_df["USG%"],
            y=highlight_df["TS%"],
            mode="markers+text",
            text=highlight_df["Player"],
            textposition="top center",

            textfont=dict(
                size=14,
                color="#ffb3c7",
                family=BOLD_FONT
            ),

            marker=dict(
                size=highlight_df["PER"].clip(lower=5, upper=35) * 1.5,
                color="#ffb3c7",
                opacity=0.98,

                line=dict(
                    width=4,
                    color="#ffe5ee"
                )
            ),

            customdata=highlight_df[[
                "Team", "GP", "MPG", "PPG",
                "PER", "AST%", "TOV%",
                "ORtg", "DRtg"
            ]],

            hovertemplate=
                "<b>%{text}</b><br>" +
                "Takım: %{customdata[0]}<br>" +
                "Maç: %{customdata[1]:.0f}<br>" +
                "Dakika: %{customdata[2]:.1f}<br>" +
                "Sayı: %{customdata[3]:.1f}<br>" +
                "USG%: %{x:.1f}<br>" +
                "TS%: %{y:.1f}<br>" +
                "PER: %{customdata[4]:.1f}<br>" +
                "AST%: %{customdata[5]:.1f}<br>" +
                "TOV%: %{customdata[6]:.1f}<br>" +
                "ORtg: %{customdata[7]:.1f}<br>" +
                "DRtg: %{customdata[8]:.1f}<extra></extra>",

            showlegend=False
        ))

    # TITLE
    if selected_team == "Tüm Takımlar":

        chart_title = "MIN. 8 MAÇ & 8 SAYI: USAGE % vs TRUE SHOOTING %"

    else:

        chart_title = (
            f"{selected_team}: TÜM OYUNCULAR — "
            "USAGE % vs TRUE SHOOTING %"
        )

    fig.update_layout(

        title=dict(
            text=chart_title,
            x=0.5,
            y=0.985,
            xanchor="center",

            font=dict(
                size=17,
                color="#dce8ff",
                family=BOLD_FONT
            )
        ),

        height=760,

        plot_bgcolor="rgba(255,255,255,0.035)",
        paper_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#eef3ff",
            family=FONT
        ),

        showlegend=False,

        xaxis=dict(
            title=dict(
                text="Usage Rate (USG%)",

                font=dict(
                    size=20,
                    color="#eef3ff",
                    family=BOLD_FONT
                )
            ),

            tickfont=dict(
                size=16,
                color="#eef3ff",
                family=BOLD_FONT
            ),

            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,

            linecolor="rgba(255,255,255,0.42)",
            linewidth=2,
            mirror=True,

            automargin=True
        ),

        yaxis=dict(
            title=dict(
                text="True Shooting % (TS%)",

                font=dict(
                    size=20,
                    color="#eef3ff",
                    family=BOLD_FONT
                )
            ),

            tickfont=dict(
                size=16,
                color="#eef3ff",
                family=BOLD_FONT
            ),

            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,

            linecolor="rgba(255,255,255,0.42)",
            linewidth=2,
            mirror=True,

            automargin=True
        ),

        margin=dict(
            l=110,
            r=130,
            t=135,
            b=90
        )
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

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # COMPARE TABLE
    if st.session_state.compare_players:

        st.subheader("⚔️ Oyuncu Karşılaştırma")

        compare_df = active_df[
            active_df["Player"].isin(
                st.session_state.compare_players
            )
        ][[
            "Player", "Team", "GP", "MPG",
            "PPG", "USG%", "TS%",
            "AST%", "TOV%", "PER",
            "ORtg", "DRtg"
        ]].sort_values("USG%", ascending=False)

        for col in [
            "GP", "MPG", "PPG", "USG%",
            "TS%", "AST%", "TOV%",
            "PER", "ORtg", "DRtg"
        ]:

            compare_df[col] = compare_df[col].round(1)

        st.dataframe(
            compare_df,
            use_container_width=True,
            hide_index=True
        )

    # MAIN TABLE
    st.subheader("Oyuncu Tablosu")

    table_df = active_df[[
        "Player", "Team", "GP", "MPG",
        "PPG", "USG%", "TS%",
        "AST%", "TOV%",
        "PER", "ORtg", "DRtg"
    ]].sort_values(
        ["USG%", "TS%"],
        ascending=False
    )

    for col in [
        "GP", "MPG", "PPG", "USG%",
        "TS%", "AST%", "TOV%",
        "PER", "ORtg", "DRtg"
    ]:

        table_df[col] = table_df[col].round(1)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )