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

df = df[
    (df["GP"] >= 8) &
    (df["MPG"] >= 10) &
    (df["PPG"] >= 5) &
    (df["FGA"] > 0)
].copy()

st.markdown("""
<style>
* {
    font-family: Arial, Helvetica, sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #f8fbff 0%, #dbeafe 55%, #f1f5f9 100%);
}

.block-container {
    padding-top: 1.4rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

h1, h2, h3, p, label, div, span {
    color: #0f172a !important;
}

h1, h2, h3,
.card-title,
.selected-pill,
.suggestion-title {
    font-family: Arial Black, Arial, Helvetica, sans-serif !important;
}

h1 {
    font-size: 2rem !important;
    font-weight: 900 !important;
}

.info-card {
    background: rgba(255,255,255,0.84);
    border: 1px solid #bfdbfe;
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 18px 40px rgba(15,23,42,0.08);
}

.card-title {
    font-size: 19px;
    font-weight: 900;
    margin-bottom: 12px;
}

.selected-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 13px;
    border-radius: 999px;
    background: #dbeafe;
    font-weight: 900;
    line-height: 1.5;
}

.suggestion-title {
    font-weight: 900;
    margin-top: 14px;
    margin-bottom: 8px;
}

.chart-card {
    background: white;
    border: 1px solid #bfdbfe;
    border-radius: 28px;
    padding: 16px;
    box-shadow: 0 24px 60px rgba(15,23,42,0.12);
    overflow: hidden;
}

div[data-testid="stTextInput"] input {
    background: white !important;
    color: #0f172a !important;
    border: 2px solid #93c5fd !important;
    border-radius: 15px !important;
    min-height: 46px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

div[data-testid="stButton"] button {
    background: white !important;
    color: #0f172a !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 999px !important;
    padding: 8px 13px !important;
    font-weight: 900 !important;
    width: 100%;
}

div[data-testid="stButton"] button:hover {
    background: #dbeafe !important;
}

div[data-testid="stCheckbox"] label {
    font-weight: 900 !important;
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
    teams = sorted(df["Team"].dropna().unique())

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

    if selected_team != "Tüm Takımlar":
        df = df[df["Team"] == selected_team].copy()

    players = sorted(df["Player"].dropna().unique())

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

    df["IS_HIGHLIGHTED"] = df["Player"].isin(selected_graph_players)

    if st.session_state.only_compare_graph and st.session_state.compare_players:
        graph_df = df[df["Player"].isin(st.session_state.compare_players)].copy()
    else:
        graph_df = df.copy()

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
            textfont=dict(size=8, color="#334155", family=FONT),
            marker=dict(
                size=base_df["MPG"] * 1.05,
                color=base_df["TS%"],
                colorscale="Viridis",
                showscale=True,
                opacity=0.80,
                line=dict(width=1.3, color="white"),
                colorbar=dict(
                    title=dict(text="TS%", font=dict(size=15, color="#0f172a", family=BOLD_FONT)),
                    tickfont=dict(size=13, color="#0f172a", family=FONT),
                    outlinewidth=1,
                    outlinecolor="#334155",
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
            textfont=dict(size=13, color="#dc2626", family=BOLD_FONT),
            marker=dict(
                size=highlight_df["MPG"] * 1.7,
                color="#ef4444",
                opacity=0.96,
                line=dict(width=4, color="#7f1d1d")
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

    fig.update_layout(
        title=dict(
            text="Min. 8 Maç & 5 Sayı: PPG vs True Shooting %",
            x=0.5,
            y=0.965,
            font=dict(size=22, color="#0f172a", family=BOLD_FONT)
        ),
        height=760,
        plot_bgcolor="#f8fafc",
        paper_bgcolor="white",
        font=dict(color="#0f172a", family=FONT),
        showlegend=False,
        xaxis=dict(
            title=dict(
                text="Sayı Ortalaması (PPG)",
                font=dict(size=20, color="#0f172a", family=BOLD_FONT)
            ),
            tickfont=dict(size=16, color="#0f172a", family=BOLD_FONT),
            gridcolor="rgba(37,99,235,0.18)",
            gridwidth=1,
            zeroline=False,
            linecolor="rgba(15,23,42,0.45)",
            linewidth=2,
            mirror=True,
            automargin=True
        ),
        yaxis=dict(
            title=dict(
                text="True Shooting % (TS%)",
                font=dict(size=20, color="#0f172a", family=BOLD_FONT)
            ),
            tickfont=dict(size=16, color="#0f172a", family=BOLD_FONT),
            gridcolor="rgba(37,99,235,0.18)",
            gridwidth=1,
            zeroline=False,
            linecolor="rgba(15,23,42,0.45)",
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
            gridcolor="rgba(148,163,184,0.14)"
        )
    )

    fig.update_yaxes(
        showgrid=True,
        minor=dict(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.14)"
        )
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.compare_players:
        st.subheader("⚔️ Oyuncu Karşılaştırma")

        compare_df = df[df["Player"].isin(st.session_state.compare_players)][[
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

    table_df = df[[
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