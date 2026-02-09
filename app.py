import streamlit as st
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

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
# AUTO REFRESH (UI only, NOT data)
# -------------------------------------------------
st_autorefresh(interval=1000, key="projector_refresh")

# -------------------------------------------------
# CACHED DATA LOADERS (CRITICAL)
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
# TIMER (DERIVED)
# -------------------------------------------------
def remaining_time(live):
    if not live.get("timer_start_ts"):
        return 0

    try:
        start_ts = float(live["timer_start_ts"])
        duration = int(live.get("timer_duration", 0))
    except Exception:
        return 0

    now_ts = datetime.now(timezone.utc).timestamp()
    return max(0, int(duration - (now_ts - start_ts)))

# -------------------------------------------------
# PROJECTOR SCREEN
# -------------------------------------------------
if screen == "projector":

    players_df = load_players()
    teams_df = load_teams()
    live = load_live_auction()

    seconds_left = remaining_time(live)
    team_color = live.get("leading_team_color") or "#f5c518"

    # ---------------- HEADER ----------------
    st.markdown(
        f"<h1 style='text-align:center;'>🏏 {live.get('message', 'Live Auction')}</h1>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ---------------- MAIN DISPLAY ----------------
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            f"""
            <div style="
                border:6px solid {team_color};
                border-radius:18px;
                padding:30px;
                background:linear-gradient(135deg,#1f2933,#111827);
                box-shadow:0 0 40px {team_color};
            ">
                <div style="font-size:42px;font-weight:900;">
                    {live.get("current_player_name", "Waiting for Auction")}
                </div>
                <div style="font-size:22px;margin-top:10px;color:#f5c518;">
                    Pool: {live.get("pool", "-")} | Role: {live.get("role", "-")}
                </div>
                <div style="font-size:22px;margin-top:6px;">
                    Base Price: ₹ {live.get("base_price", "-")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background:#111827;
                border-radius:16px;
                padding:30px;
                border:2px solid #2d3748;
                text-align:center;
            ">
                <div style="font-size:20px;">Current Bid</div>
                <div style="font-size:54px;font-weight:900;color:#22c55e;">
                    ₹ {live.get("current_bid", "-")}
                </div>
                <div style="margin-top:12px;font-size:20px;">
                    Leading Team
                </div>
                <div style="font-size:26px;font-weight:800;color:{team_color};">
                    {live.get("leading_team", "-")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- TIMER ----------------
    st.markdown(
        f"<div style='text-align:center;font-size:36px;font-weight:800;'>⏱ {seconds_left} sec</div>",
        unsafe_allow_html=True
    )

    # ---------------- SOLD / UNSOLD ----------------
    if live.get("status") == "SOLD":
        st.markdown(
            f"<div style='text-align:center;font-size:48px;font-weight:900;color:#22c55e;'>"
            f"SOLD to {live.get('leading_team')} for ₹ {live.get('current_bid')}</div>",
            unsafe_allow_html=True
        )

    elif live.get("status") == "UNSOLD":
        st.markdown(
            "<div style='text-align:center;font-size:48px;font-weight:900;color:#ef4444;'>UNSOLD</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ---------------- VIEWER MODALS ----------------
    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("📋 Sold Players"):
            with st.modal("Sold Players"):
                df = players_df[players_df["status"] == "SOLD"]
                st.dataframe(df[["player_name", "pool", "role", "sold_price", "sold_to"]])

    with colB:
        if st.button("❌ Unsold Players"):
            with st.modal("Unsold Players"):
                df = players_df[players_df["status"] != "SOLD"]
                st.dataframe(df[["player_name", "pool", "role", "base_price"]])

    with colC:
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
                        st.dataframe(squad[["player_name", "role", "sold_price"]])

else:
    st.title("Auction App")
    st.caption("Landing screen coming soon.")
