import streamlit as st
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

from sheets import read_sheet

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Auction Projector",
    layout="wide"
)

# -------------------------------------------------
# ROUTING
# -------------------------------------------------
screen = st.query_params.get("screen", "projector")

# -------------------------------------------------
# UI AUTO REFRESH (1 sec)
# -------------------------------------------------
st_autorefresh(interval=1000, key="projector_refresh")

# -------------------------------------------------
# CACHED DATA LOADERS (RATE SAFE)
# -------------------------------------------------
@st.cache_data(ttl=5)
def load_players():
    return read_sheet("Players")

@st.cache_data(ttl=5)
def load_teams():
    return read_sheet("Teams")

@st.cache_data(ttl=3)
def load_live_auction():
    df = read_sheet("Live_Auction")
    return dict(zip(df["key"], df["value"]))

# -------------------------------------------------
# TIMER
# -------------------------------------------------
def remaining_time(live):
    try:
        start = float(live.get("timer_start_ts", 0))
        duration = int(live.get("timer_duration", 0))
        if start == 0:
            return 0
        now = datetime.now(timezone.utc).timestamp()
        return max(0, int(duration - (now - start)))
    except Exception:
        return 0

# -------------------------------------------------
# PROJECTOR SCREEN
# -------------------------------------------------
if screen == "projector":

    players_df = load_players()
    teams_df = load_teams()
    live = load_live_auction()

    seconds_left = remaining_time(live)

    team_color = live.get("leading_team_color") or "#f5c518"
    player_name = live.get("current_player_name") or "Waiting for Auction"
    pool = live.get("pool") or "-"
    role = live.get("role") or "-"
    base_price = live.get("base_price") or "-"
    current_bid = live.get("current_bid") or "-"
    leading_team = live.get("leading_team") or "-"

    st.markdown(
        f"<h1 style='text-align:center;'>🏏 {live.get('message','Live Auction')}</h1>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -------------------------------------------------
    # HTML CARDS (NO MARKDOWN PARSING)
    # -------------------------------------------------
    html = f"""
    <div style="display:flex; gap:30px;">

        <div style="
            flex:3;
            border:6px solid {team_color};
            border-radius:18px;
            padding:30px;
            background:linear-gradient(135deg,#1f2933,#111827);
            box-shadow:0 0 40px {team_color};
            color:white;
        ">
            <div style="font-size:42px;font-weight:900;">
                {player_name}
            </div>

            <div style="font-size:22px;margin-top:10px;color:#f5c518;">
                Pool: {pool} | Role: {role}
            </div>

            <div style="font-size:22px;margin-top:6px;">
                Base Price: ₹ {base_price}
            </div>
        </div>

        <div style="
            flex:2;
            background:#111827;
            border-radius:16px;
            padding:30px;
            border:2px solid #2d3748;
            text-align:center;
            color:white;
        ">
            <div style="font-size:20px;">Current Bid</div>
            <div style="font-size:54px;font-weight:900;color:#22c55e;">
                ₹ {current_bid}
            </div>

            <div style="margin-top:12px;font-size:20px;">
                Leading Team
            </div>
            <div style="font-size:26px;font-weight:800;color:{team_color};">
                {leading_team}
            </div>
        </div>

    </div>

    <div style="text-align:center;margin-top:25px;font-size:36px;font-weight:800;">
        ⏱ {seconds_left} sec
    </div>
    """

    components.html(html, height=360)

    # -------------------------------------------------
    # SOLD / UNSOLD
    # -------------------------------------------------
    if live.get("status") == "SOLD":
        st.success(f"SOLD to {leading_team} for ₹ {current_bid}")

    elif live.get("status") == "UNSOLD":
        st.error("UNSOLD")

    st.markdown("---")

    # -------------------------------------------------
    # VIEWER MODALS
    # -------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Sold Players"):
            with st.modal("Sold Players"):
                df = players_df[players_df["status"] == "SOLD"]
                st.dataframe(df[["player_name","pool","role","sold_price","sold_to"]])

    with col2:
        if st.button("❌ Unsold Players"):
            with st.modal("Unsold Players"):
                df = players_df[players_df["status"] != "SOLD"]
                st.dataframe(df[["player_name","pool","role","base_price"]])

    with col3:
        if st.button("🏏 Team Squads"):
            with st.modal("Team Squads"):
                for _, team in teams_df.iterrows():
                    st.markdown(
                        f"<h3 style='color:{team['team_color']}'>{team['team_name']}</h3>",
                        unsafe_allow_html=True
                    )
                    squad = players_df[players_df["sold_to"] == team["team_name"]]
                    if squad.empty:
                        st.caption("No players yet")
                    else:
                        st.dataframe(squad[["player_name","role","sold_price"]])

else:
    st.title("Auction App")
    st.caption("Landing screen coming next.")
