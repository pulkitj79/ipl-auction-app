import streamlit as st
from datetime import datetime, timezone

from sheets import read_sheet, write_kv, update_row

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def utc_now():
    return int(datetime.now(timezone.utc).timestamp())

# -------------------------------------------------
# AUCTIONEER SCREEN
# -------------------------------------------------
def show_auctioneer():

    st.title("🎛 Auctioneer Control Panel")

    # ---------------- AUTH ----------------
    access_df = read_sheet("Config_Access")
    access = dict(zip(access_df["key"], access_df["value"]))
    pin_required = str(access.get("auctioneer_pin"))

    entered_pin = st.text_input("Enter Auctioneer PIN", type="password")

    if entered_pin != pin_required:
        st.info("Enter Auctioneer PIN to continue")
        st.stop()

    st.success("Authenticated")
    st.markdown("---")

    # ---------------- LOAD DATA ----------------
    players_df = read_sheet("Players")
    live_df = read_sheet("Live_Auction")
    live = dict(zip(live_df["key"], live_df["value"]))

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

    # ---------------- NEXT PLAYER (PLACEHOLDER) ----------------
    st.subheader("Next Player")

    st.caption(
        "Random player selection + timer start "
        "will be reattached here next."
    )
