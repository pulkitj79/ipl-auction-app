import streamlit as st
import time
from datetime import datetime, timezone

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
query_params = st.experimental_get_query_params()
screen = query_params.get("screen", ["projector"])[0]

# -------------------------------------------------
# LOAD DATA HELPERS
# -------------------------------------------------
def load_live_auction():
    df = read_sheet("Live_Auction")
    return dict(zip(df["key"], df["value"]))


def remaining_time(live):
    if not live.get("timer_start_ts"):
        return 0

    try:
        start_ts = float(live["timer_start_ts"])
        duration = int(live.get("timer_duration", 0))
    except Exception:
        return 0

    now_ts = datetime.now(timezone.utc).timestamp()
    remaining = duration - (now_ts - start_ts)
    return max(0, int(remaining))


# -------------------------------------------------
# PROJECTOR SCREEN
# -------------------------------------------------
if screen == "projector":

    # auto refresh every second (needed for timer)
    st.experimental_set_query_params(screen="projector")
    time.sleep(1)
    st.experimental_rerun()

    # load sheets
    players_df = read_sheet("Players")
    teams_df = read_sheet("Teams")
    live = load_live_auction()

    seconds_left = remaining_time(live)

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    st.markdown(
        f"""
        <h1 style="text-align:center;">
            🏏 {live.get("message", "Live Auction")}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -------------------------------------------------
    # MAIN DISPLAY
    # -------------------------------------------------
    team_color = live.get("leading_team_color") or "#f5c518"

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
                    Pool: {live.get("pool", "-")} |
                    Role: {live.get("role", "-")}
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

    # -------------------------------------------------
    # TIMER
    # -------------------------------------------------
    st.markdown(
        f"""
        <div style="text-align:center;margin-top:20px;">
            <span style="font-size:36px;font-weight:800;">
                ⏱ {seconds_left} sec
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # SOLD / UNSOLD STATE
    # -------------------------------------------------
    if live.get("status") == "SOLD":
        st.markdown(
            f"""
            <div style="
                margin-top:30px;
                font-size:48px;
                font-weight:900;
                color:#22c55e;
                text-align:center;
            ">
                SOLD to {live.get("leading_team")} for ₹ {live.get("current_bid")}
            </div>
            """,
            unsafe_allow_html=True
        )

    if live.get("status") == "UNSOLD":
        st.markdown(
            """
            <div style="
                margin-top:30px;
                font-size:48px;
                font-weight:900;
                color:#ef4444;
                text-align:center;
            ">
                UNSOLD
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # -------------------------------------------------
    # VIEWER MODALS (LOCAL ONLY)
    # -------------------------------------------------
    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("📋 Sold Players"):
            with st.modal("Sold Players"):
                sold_df = players_df[players_df["status"] == "SOLD"]
                st.dataframe(
                    sold_df[
                        ["player_name", "pool", "role", "sold_price", "sold_to"]
                    ],
                    use_container_width=True
                )

    with colB:
        if st.button("❌ Unsold Players"):
            with st.modal("Unsold Players"):
                unsold_df = players_df[players_df["status"] != "SOLD"]
                st.dataframe(
                    unsold_df[
                        ["player_name", "pool", "role", "base_price"]
                    ],
                    use_container_width=True
                )

    with colC:
        if st.button("🏏 Team Squads"):
            with st.modal("Team Squads"):
                for _, team in teams_df.iterrows():
                    st.markdown(
                        f"""
                        <h3 style="color:{team['team_color']};">
                            {team['team_name']}
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )

                    team_players = players_df[
                        players_df["sold_to"] == team["team_name"]
                    ]

                    if team_players.empty:
                        st.caption("No players yet")
                    else:
                        st.dataframe(
                            team_players[
                                ["player_name", "role", "sold_price"]
                            ],
                            use_container_width=True
                        )

# -------------------------------------------------
# FALLBACK
# -------------------------------------------------
else:
    st.title("Auction App")
    st.caption("Landing screen will be added later.")
