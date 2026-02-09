import streamlit as st
import random
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

from sheets import read_sheet, write_kv, update_row, append_row

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Auction Control",
    layout="wide"
)

# -------------------------------------------------
# ROUTING
# -------------------------------------------------
screen = st.query_params.get("screen", "projector")

# -------------------------------------------------
# AUTO REFRESH (UI ONLY)
# -------------------------------------------------
st_autorefresh(interval=1000, key="ui_refresh")

# -------------------------------------------------
# CACHED READS
# -------------------------------------------------
@st.cache_data(ttl=5)
def load_players():
    return read_sheet("Players")

@st.cache_data(ttl=5)
def load_teams():
    return read_sheet("Teams")

@st.cache_data(ttl=3)
def load_live():
    df = read_sheet("Live_Auction")
    return dict(zip(df["key"], df["value"]))

@st.cache_data(ttl=30)
def load_config_pool_rules():
    return read_sheet("Config_Pool_Rules")

@st.cache_data(ttl=60)
def load_access_config():
    return dict(zip(
        read_sheet("Config_Access")["key"],
        read_sheet("Config_Access")["value"]
    ))

# -------------------------------------------------
# TIMER UTILITY
# -------------------------------------------------
def utc_now():
    return int(datetime.now(timezone.utc).timestamp())

# =================================================
# AUCTIONEER SCREEN
# =================================================
if screen == "auctioneer":

    st.title("🎛 Auctioneer Control Panel")

    # ---------------- AUTH ----------------
    access = load_access_config()
    pin_required = access.get("auctioneer_pin")

    entered_pin = st.text_input(
        "Enter Auctioneer PIN",
        type="password"
    )

    if entered_pin != str(pin_required):
        st.warning("Enter valid Auctioneer PIN")
        st.stop()

    # ---------------- LOAD DATA ----------------
    players_df = load_players()
    live = load_live()
    pool_rules = load_config_pool_rules()

    st.markdown("---")

    # ---------------- POOL SELECTION ----------------
    st.subheader("Pool Selection")

    if not live.get("active_pool"):
        pool = st.selectbox("Select Pool", ["A", "B", "FINAL"])

        if st.button("🔒 Lock Pool"):
            write_kv("Live_Auction", "active_pool", pool)
            write_kv("Live_Auction", "status", "IDLE")
            st.success(f"Pool {pool} locked")

    else:
        st.info(f"Active Pool: {live.get('active_pool')} (locked)")

    st.markdown("---")

    # ---------------- NEXT PLAYER ----------------
    st.subheader("Next Player")

    active_pool = live.get("active_pool")

    if active_pool:
        available = players_df[
            (players_df["pool"] == active_pool) &
            (players_df["status"] == "AVAILABLE")
        ]

        if available.empty:
            st.warning("No players left in this pool")
        else:
            if st.button("🎲 Pick Random Player"):
                player = available.sample(1).iloc[0]

                rule = pool_rules[pool_rules["pool"] == active_pool].iloc[0]
                timer_seconds = int(rule["timer_seconds"])

                write_kv("Live_Auction", "current_player_id", player["player_id"])
                write_kv("Live_Auction", "current_player_name", player["player_name"])
                write_kv("Live_Auction", "pool", player["pool"])
                write_kv("Live_Auction", "role", player["role"])
                write_kv("Live_Auction", "image_url", player["image_url"])
                write_kv("Live_Auction", "base_price", player["base_price"])
                write_kv("Live_Auction", "current_bid", player["base_price"])
                write_kv("Live_Auction", "leading_team", "")
                write_kv("Live_Auction", "leading_team_color", "")
                write_kv("Live_Auction", "bid_count", 0)
                write_kv("Live_Auction", "timer_start_ts", utc_now())
                write_kv("Live_Auction", "timer_duration", timer_seconds)
                write_kv("Live_Auction", "no_bid_teams", "")
                write_kv("Live_Auction", "status", "LIVE")
                write_kv("Live_Auction", "message", "Bidding Open")

                update_row(
                    "Players",
                    "player_id",
                    player["player_id"],
                    {"status": "IN_AUCTION"}
                )

                st.success(f"Auction started for {player['player_name']}")

    st.markdown("---")

    # ---------------- CLOSE AUCTION ----------------
    st.subheader("Close Auction")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔨 SOLD"):
            write_kv("Live_Auction", "status", "SOLD")
            write_kv("Live_Auction", "message", "SOLD")

            append_row("Auction_Log", {
                "timestamp": utc_now(),
                "player_id": live.get("current_player_id"),
                "action": "SOLD",
                "team_name": live.get("leading_team"),
                "bid_amount": live.get("current_bid"),
                "round": live.get("active_pool")
            })

            update_row(
                "Players",
                "player_id",
                live.get("current_player_id"),
                {
                    "status": "SOLD",
                    "sold_to": live.get("leading_team"),
                    "sold_price": live.get("current_bid"),
                    "round": live.get("active_pool")
                }
            )

            st.success("Player SOLD")

    with col2:
        if st.button("❌ UNSOLD"):
            write_kv("Live_Auction", "status", "UNSOLD")
            write_kv("Live_Auction", "message", "UNSOLD")

            update_row(
                "Players",
                "player_id",
                live.get("current_player_id"),
                {
                    "status": "UNSOLD",
                    "round": live.get("active_pool")
                }
            )

            append_row("Auction_Log", {
                "timestamp": utc_now(),
                "player_id": live.get("current_player_id"),
                "action": "UNSOLD",
                "team_name": "",
                "bid_amount": "",
                "round": live.get("active_pool")
            })

            st.warning("Player UNSOLD")

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
