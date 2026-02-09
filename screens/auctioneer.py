import streamlit as st
from sheets import read_sheet, write_kv, update_row

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_live():
    df = read_sheet("Live_Auction")
    return dict(zip(df["key"], df["value"]))

def bump_refresh_token(live):
    current = int(live.get("refresh_token", 0))
    write_kv("Live_Auction", "refresh_token", current + 1)

# -------------------------------------------------
# AUCTIONEER SCREEN
# -------------------------------------------------
def show_auctioneer():

    st.title("🎛 Auctioneer Control Panel")

    # ---------- AUTH ----------
    access_df = read_sheet("Config_Access")
    access = dict(zip(access_df["key"], access_df["value"]))
    pin_required = str(access.get("auctioneer_pin"))

    entered_pin = st.text_input("Enter Auctioneer PIN", type="password")

    if entered_pin != pin_required:
        st.info("Enter Auctioneer PIN to continue")
        st.stop()

    st.success("Authenticated")
    st.markdown("---")

    # ---------- LOAD DATA ----------
    players_df = read_sheet("Players")
    live = get_live()

    # ---------- POOL SELECTION ----------
    st.subheader("Pool Selection")

    if not live.get("active_pool"):
        pool = st.selectbox("Select Pool", ["A", "B", "FINAL"])

        if st.button("🔒 Lock Pool"):
            write_kv("Live_Auction", "active_pool", pool)
            write_kv("Live_Auction", "status", "IDLE")
            write_kv("Live_Auction", "message", f"Pool {pool} Locked")

            bump_refresh_token(live)
            st.success(f"Pool {pool} locked")

    else:
        st.info(f"Active Pool: {live.get('active_pool')} (locked)")

    st.markdown("---")

    # ---------- NEXT PLAYER ----------
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

                # Update Live_Auction
                write_kv("Live_Auction", "current_player_id", player["player_id"])
                write_kv("Live_Auction", "current_player_name", player["player_name"])
                write_kv("Live_Auction", "pool", player["pool"])
                write_kv("Live_Auction", "role", player["role"])
                write_kv("Live_Auction", "base_price", player["base_price"])
                write_kv("Live_Auction", "current_bid", player["base_price"])
                write_kv("Live_Auction", "leading_team", "")
                write_kv("Live_Auction", "leading_team_color", "")
                write_kv("Live_Auction", "status", "LIVE")
                write_kv("Live_Auction", "message", "Bidding Open")
                write_kv("Live_Auction", "last_action", "NEXT_PLAYER")

                # Update Player status
                update_row(
                    "Players",
                    "player_id",
                    player["player_id"],
                    {"status": "IN_AUCTION"}
                )

                bump_refresh_token(live)
                st.success(f"Auction started for {player['player_name']}")

    st.markdown("---")

    # ---------- CLOSE AUCTION ----------
    st.subheader("Close Auction")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔨 SOLD"):
            write_kv("Live_Auction", "status", "SOLD")
            write_kv("Live_Auction", "message", "SOLD")
            write_kv("Live_Auction", "last_action", "SOLD")

            bump_refresh_token(live)
            st.success("Player marked SOLD")

    with col2:
        if st.button("❌ UNSOLD"):
            write_kv("Live_Auction", "status", "UNSOLD")
            write_kv("Live_Auction", "message", "UNSOLD")
            write_kv("Live_Auction", "last_action", "UNSOLD")

            bump_refresh_token(live)
            st.warning("Player marked UNSOLD")
