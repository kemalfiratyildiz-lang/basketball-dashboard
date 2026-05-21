import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="EuroLeague Creator Map",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(245, 158, 11, 0.22), transparent 28%),
        radial-gradient(circle at bottom right, rgba(124, 58, 237, 0.22), transparent 30%),
        linear-gradient(135deg, #120d08 0%, #17120b 45%, #0b0b12 100%);
    color: #f8ead0;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #1a1208 0%, #0f172a 100%);
    border-right: 1px solid rgba(251, 191, 36, 0.25);
    min-width: 210px !important;
    max-width: 210px !important;
}

[data-testid="stSidebar"] > div {
    padding-left: 1rem;
    padding-right: 0.7rem;
}

h1, h2, h3, p, label, span, div {
    font-family: Arial, Helvetica, sans-serif;
}

h1 {
    color: #fff3dc;
    font-weight: 900;
}

h2, h3 {
    color: #fbbf24;
}

p, label, span, div {
    color: #f8ead0;
}

[data-testid="stMetric"] {
    background: rgba(31, 23, 12, 0.78);
    padding: 18px;
    border-radius: 20px;
    border: 1px solid rgba(251, 191, 36, 0.25);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

[data-testid="stMetricValue"] {
    color: #fbbf24;
    font-weight: 900;
}

[data-testid="stMetricLabel"] {
    color: #f8ead0;
    font-weight: 700;
}

/* Sidebar başlık */
section[data-testid="stSidebar"] h1 {
    font-size: 22px !important;
    line-height: 1.1;
}

/* Checkboxları radio gibi yuvarlak yap */
.stCheckbox {
    margin-bottom: -6px;
}

.stCheckbox label {
    color: #f8ead0 !important;
    font-weight: 700;
    font-size: 14px !important;
}

.stCheckbox input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    width: 16px !important;
    height: 16px !important;
    border-radius: 50% !important;
    border: 2px solid rgba(248, 234, 208, 0.35) !important;
    background: rgba(15, 23, 42, 0.55) !important;
    position: relative;
    cursor: pointer;
}

.stCheckbox input[type="checkbox"]:checked {
    background: #ff4b4b !important;
    border-color: #ff4b4b !important;
}

.stCheckbox input[type="checkbox"]:checked::after {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: white;
    position: absolute;
    top: 3px;
    left: 3px;
}

.stMultiSelect label {
    color: #f8ead0 !important;
    font-weight: 700;
}

section[data-testid="stSidebar"] div {
    color: #f8ead0;
}

input {
    background-color: #374151 !important;
    color: #f8ead0 !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 16px;
    border: 1px solid rgba(251, 191, 36, 0.22);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA
# =====================================================
df = pd.read_csv("euroleague_merged_dashboard_data.csv")
df.columns = df.columns.str.strip()

df["Player"] = df["Player"].astype(str).str.strip()
df["Team"] = df["Team"].astype(str).str.strip()

df.loc[df["Team"] == "LYV", "Team"] = "ASV"

paris_players = [
    "NADIR HIFI", "JUSTIN ROBINSON", "JARED RHODEN", "LAMAR STEVENS",
    "AMATH MBAYE", "AMATH M'BAYE", "SEBASTIAN HERRERA",
    "ALLAN JULIAN DOKOSSI", "ALLAN JULIEN DOKOSSI",
    "MOUHAMED FAYE", "MOUHAMMED FAYE", "DEREK WILLIS",
    "COLLIN MALCOLM", "TYSON WARD", "LEOPOLD CAVALIERE"
]

df.loc[df["Player"].str.upper().isin(paris_players), "Team"] = "PARI"

# =====================================================
# KOLON BULUCU
# =====================================================
def find_col(names):
    for col in df.columns:
        clean_col = (
            col.lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
            .replace("%", "")
        )

        for name in names:
            clean_name = (
                name.lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
                .replace("%", "")
            )

            if clean_col == clean_name:
                return col

    return None


player_col = find_col(["Player"])
team_col = find_col(["Team"])
gp_col = find_col(["GP", "G", "Games"])
mpg_col = find_col(["MPG", "MIN", "Minutes", "Minutes Per Game"])

ast_pct_col = find_col(["AST%", "Assist%", "AST Pct"])
tov_pct_col = find_col(["TOV%", "TO%", "Turnover%", "TOV Pct"])

ast_col = find_col(["AST", "Assists", "Assist"])
tov_col = find_col(["TOV", "TO", "Turnovers", "Turnover"])

if ast_col == ast_pct_col:
    ast_col = None

if tov_col == tov_pct_col:
    tov_col = None

usg_col = find_col(["USG%", "USG", "Usage", "Usage Rate"])
net_col = find_col(["NetRtg", "Net Rating", "NETRTG"])
ortg_col = find_col(["ORtg", "ORTG", "Offensive Rating"])
drtg_col = find_col(["DRtg", "DRTG", "Defensive Rating"])
ts_col = find_col(["TS%", "TS"])

required = {
    "Player": player_col,
    "Team": team_col,
    "GP": gp_col,
    "MPG": mpg_col,
    "AST%": ast_pct_col,
    "TOV%": tov_pct_col,
    "USG%": usg_col
}

missing = [k for k, v in required.items() if v is None]

if missing:
    st.error(f"Eksik kolon bulundu: {missing}")
    st.write(df.columns.tolist())
    st.stop()

# =====================================================
# SAYISAL TEMİZLİK
# =====================================================
numeric_cols = [
    gp_col,
    mpg_col,
    ast_pct_col,
    tov_pct_col,
    ast_col,
    tov_col,
    usg_col,
    net_col,
    ortg_col,
    drtg_col,
    ts_col
]

numeric_cols = [c for c in numeric_cols if c is not None]
numeric_cols = list(dict.fromkeys(numeric_cols))

for col in numeric_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

for col in [ast_pct_col, tov_pct_col, usg_col, ts_col]:
    if col:
        max_val = df[col].dropna().max()

        if max_val <= 1:
            df[col] = df[col] * 100
        elif max_val > 100:
            df[col] = df[col] / 10

df = df.dropna(subset=[gp_col, mpg_col, ast_pct_col, tov_pct_col, usg_col])

df = df[
    (df[gp_col] >= 8) &
    (df[mpg_col] >= 8)
].copy()

# =====================================================
# HESAPLAMALAR
# =====================================================
df["AST/TOV Index"] = df[ast_pct_col] / df[tov_pct_col].replace(0, pd.NA)
df["AST/TOV Index"] = df["AST/TOV Index"].fillna(0)

df["Bubble Size"] = df[usg_col]

# =====================================================
# SIDEBAR
# =====================================================
teams = sorted(df[team_col].dropna().unique())

if "all_teams_toggle" not in st.session_state:
    st.session_state["all_teams_toggle"] = True

for team in teams:
    key = f"team_check_{team}"
    if key not in st.session_state:
        st.session_state[key] = True


def toggle_all_teams():
    value = st.session_state["all_teams_toggle"]
    for team in teams:
        st.session_state[f"team_check_{team}"] = value


st.sidebar.title("🏀 Takım Filtrele")

st.sidebar.checkbox(
    "Tüm Takımlar",
    key="all_teams_toggle",
    on_change=toggle_all_teams
)

selected_teams = []

for team in teams:
    if st.sidebar.checkbox(team, key=f"team_check_{team}"):
        selected_teams.append(team)

st.sidebar.markdown("---")

players = sorted(df[player_col].dropna().unique())

selected_players = st.sidebar.multiselect(
    "Oyuncu seç / karşılaştır",
    players,
    placeholder="Oyuncu ara..."
)

if not selected_teams:
    st.warning("En az bir takım seçmelisin.")
    st.stop()

filtered = df[df[team_col].isin(selected_teams)].copy()

avg_ast_pct = filtered[ast_pct_col].mean()
avg_tov_pct = filtered[tov_pct_col].mean()

# =====================================================
# BAŞLIK
# =====================================================
st.title("🏀 EuroLeague Creator Map")

st.markdown("""
**Assist% vs Turnover%** üzerinden oyuncuların oyun kurma kalitesini gösteren interaktif harita.

- **Yukarı çıktıkça:** asist üretimi artar  
- **Sola gittikçe:** top kaybı riski azalır  
- **Daire büyüklüğü:** Usage%
""")

# =====================================================
# METRİKLER
# =====================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Oyuncu", len(filtered))
c2.metric("Ortalama AST%", f"{filtered[ast_pct_col].mean():.1f}%")
c3.metric("Ortalama TOV%", f"{filtered[tov_pct_col].mean():.1f}%")
c4.metric("AST/TOV Index", f"{filtered['AST/TOV Index'].mean():.2f}")

# =====================================================
# ORTAK HOVER
# =====================================================
hover_cols = [
    team_col,
    gp_col,
    mpg_col,
    ast_pct_col,
    tov_pct_col,
    "AST/TOV Index",
    ast_col,
    tov_col,
    usg_col,
    ts_col,
    net_col,
    ortg_col,
    drtg_col
]

hover_cols = [c for c in hover_cols if c is not None]
hover_cols = list(dict.fromkeys(hover_cols))


def build_hover_template(cols):
    template = "<b>%{text}</b><br>"
    template += f"Team: %{{customdata[{cols.index(team_col)}]}}<br>"
    template += f"GP: %{{customdata[{cols.index(gp_col)}]}}<br>"
    template += f"MPG: %{{customdata[{cols.index(mpg_col)}]:.1f}}<br>"
    template += f"AST%: %{{customdata[{cols.index(ast_pct_col)}]:.1f}}%<br>"
    template += f"TOV%: %{{customdata[{cols.index(tov_pct_col)}]:.1f}}%<br>"
    template += f"AST/TOV Index: %{{customdata[{cols.index('AST/TOV Index')}]:.2f}}<br>"

    if ast_col and ast_col in cols:
        template += f"AST Ort.: %{{customdata[{cols.index(ast_col)}]:.1f}}<br>"

    if tov_col and tov_col in cols:
        template += f"TOV Ort.: %{{customdata[{cols.index(tov_col)}]:.1f}}<br>"

    if usg_col and usg_col in cols:
        template += f"USG%: %{{customdata[{cols.index(usg_col)}]:.1f}}%<br>"

    if ts_col and ts_col in cols:
        template += f"TS%: %{{customdata[{cols.index(ts_col)}]:.1f}}%<br>"

    if net_col and net_col in cols:
        template += f"Net Rating: %{{customdata[{cols.index(net_col)}]:.1f}}<br>"

    if ortg_col and ortg_col in cols:
        template += f"ORtg: %{{customdata[{cols.index(ortg_col)}]:.1f}}<br>"

    if drtg_col and drtg_col in cols:
        template += f"DRtg: %{{customdata[{cols.index(drtg_col)}]:.1f}}<br>"

    template += "<extra></extra>"
    return template


hovertemplate = build_hover_template(hover_cols)

# =====================================================
# ANA GRAFİK
# =====================================================
fig = px.scatter(
    filtered,
    x=tov_pct_col,
    y=ast_pct_col,
    size="Bubble Size",
    color=team_col,
    text=player_col,
    custom_data=hover_cols,
    template="plotly_dark",
    size_max=38,
    title="Assist% / Turnover% Creator Map",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig.update_traces(
    hovertemplate=hovertemplate,
    textposition="top center",
    textfont=dict(size=9, color="#f8ead0"),
    marker=dict(
        opacity=0.82,
        line=dict(width=1.2, color="rgba(255,255,255,0.45)")
    )
)

fig.add_vline(
    x=avg_tov_pct,
    line_dash="dash",
    line_color="#f59e0b",
    annotation_text=f"Ort. TOV%: {avg_tov_pct:.1f}",
    annotation_position="top"
)

fig.add_hline(
    y=avg_ast_pct,
    line_dash="dash",
    line_color="#f59e0b",
    annotation_text=f"Ort. AST%: {avg_ast_pct:.1f}",
    annotation_position="right"
)

fig.update_layout(
    height=790,
    paper_bgcolor="rgba(18, 13, 8, 0.75)",
    plot_bgcolor="rgba(15, 15, 18, 0.78)",
    font=dict(
        family="Arial, Helvetica, sans-serif",
        size=14,
        color="#f8ead0"
    ),
    title=dict(
        font=dict(size=25, color="#fbbf24"),
        x=0.5
    ),
    legend_title_text="Takım",
    margin=dict(l=40, r=40, t=80, b=40)
)

fig.update_xaxes(
    title="Turnover%",
    ticksuffix="%",
    tickformat=".1f",
    gridcolor="rgba(255,255,255,0.13)",
    zeroline=False
)

fig.update_yaxes(
    title="Assist%",
    ticksuffix="%",
    tickformat=".1f",
    gridcolor="rgba(255,255,255,0.13)",
    zeroline=False
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABLOLAR
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "En İyi AST/TOV Oyuncuları",
    "Seçili Oyuncu Karşılaştırması",
    "Tüm Oyuncu Tablosu"
])

table_cols = [
    player_col,
    team_col,
    gp_col,
    mpg_col,
    ast_pct_col,
    tov_pct_col,
    "AST/TOV Index",
    ast_col,
    tov_col,
    usg_col,
    ts_col,
    net_col,
    ortg_col,
    drtg_col
]

table_cols = [c for c in table_cols if c is not None]
table_cols = list(dict.fromkeys(table_cols))

with tab1:
    show_table = (
        filtered[table_cols]
        .sort_values("AST/TOV Index", ascending=False)
        .head(30)
        .copy()
    )

    for col in show_table.columns:
        if col not in [player_col, team_col]:
            show_table[col] = show_table[col].round(1)

    st.dataframe(show_table, use_container_width=True, hide_index=True)

with tab2:
    if selected_players:
        selected_df = filtered[filtered[player_col].isin(selected_players)].copy()

        compare_table = selected_df[table_cols].copy()

        for col in compare_table.columns:
            if col not in [player_col, team_col]:
                compare_table[col] = compare_table[col].round(1)

        st.dataframe(compare_table, use_container_width=True, hide_index=True)

        compare_fig = px.scatter(
            selected_df,
            x=tov_pct_col,
            y=ast_pct_col,
            size="Bubble Size",
            color=team_col,
            text=player_col,
            custom_data=hover_cols,
            template="plotly_dark",
            size_max=55,
            title="Seçili Oyuncular Karşılaştırması",
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        compare_fig.update_traces(
            hovertemplate=hovertemplate,
            textposition="top center",
            textfont=dict(size=11, color="#f8ead0"),
            marker=dict(
                opacity=0.9,
                line=dict(width=1.5, color="rgba(255,255,255,0.65)")
            )
        )

        compare_fig.update_layout(
            height=520,
            paper_bgcolor="rgba(18, 13, 8, 0.75)",
            plot_bgcolor="rgba(15, 15, 18, 0.78)",
            font=dict(color="#f8ead0"),
            title=dict(font=dict(color="#fbbf24"))
        )

        compare_fig.update_xaxes(
            title="Turnover%",
            ticksuffix="%",
            tickformat=".1f",
            gridcolor="rgba(255,255,255,0.13)",
            zeroline=False
        )

        compare_fig.update_yaxes(
            title="Assist%",
            ticksuffix="%",
            tickformat=".1f",
            gridcolor="rgba(255,255,255,0.13)",
            zeroline=False
        )

        st.plotly_chart(compare_fig, use_container_width=True)

    else:
        st.info("Karşılaştırma için soldan oyuncu seç.")

with tab3:
    all_table = filtered[table_cols].copy()

    for col in all_table.columns:
        if col not in [player_col, team_col]:
            all_table[col] = all_table[col].round(1)

    st.dataframe(all_table, use_container_width=True, hide_index=True)

st.caption("Filtre: minimum 8 maç ve 8 dakika. Daire büyüklüğü: Usage%.")