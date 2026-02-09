import streamlit as st
import streamlit.components.v1 as components
from sheets import read_sheet

# -------------------------------------------------
# PROJECTOR SCREEN (EVENT DRIVEN)
# -------------------------------------------------
def show_projector():

    st.set_page_config(layout="wide")

    # -------- Session State --------
    st.session_state.setdefault("last_refresh_token", None)
    st.session_state.setdefault("cached_live", None)

    # -------- Manual Refresh Button (safe) --------
    refresh_clicked = st.button("🔄 Refresh")

    # -------- Read Live_Auction --------
    live_df = read_sheet("Live_Auction")
    live = dict(zip(live_df["key"], live_df["value"]))
    token = live.get("refresh_token")

    # -------- Detect Change --------
    if (
        refresh_clicked
        or st.session_state["last_refresh_token"] != token
        or st.session_state["cached_live"] is None
    ):
        st.session_state["cached_live"] = live
        st.session_state["last_refresh_token"] = token

    live = st.session_state["cached_live"]

    # -------- Derived Values --------
    team_color = live.get("leading_team_color") or "#f5c518"

    player_name = live.get("current_player_name") or "Waiting for Auction"
    pool = live.get("pool") or "-"
    role = live.get("role") or "-"
    base_price = live.get("base_price") or "-"
    current_bid = live.get("current_bid") or "-"
    leading_team = live.get("leading_team") or "-"

    # -------- Header --------
    st.markdown(
        f"<h1 style='text-align:center;'>🏏 {live.get('message','Live Auction')}</h1>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -------- Main UI (HTML, stable) --------
    html = f"""
    <div style="display:flex; gap:30px;">

        <div style="
            flex:3;
            border:6px solid {team_color};
            border-radius:18px;
            padding:30px;
            background:#111827;
            box-shadow:0 0 30px {team_color};
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
            background:#0f172a;
            border-radius:16px;
            padding:30px;
            border:2px solid #334155;
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
    """

    components.html(html, height=360)

    # -------- SOLD / UNSOLD --------
    if live.get("status") == "SOLD":
        st.success(f"SOLD to {leading_team} for ₹ {current_bid}")
    elif live.get("status") == "UNSOLD":
        st.error("UNSOLD")
