import streamlit as st
from sheets import read_sheet, write_kv

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
# BIDDER SCREEN
# -------------------------------------------------
def show_bidder():

    st.title("📱 Bidder Screen")

    # ---------- AUTH ----------
    teams_df = read_sheet("Teams")

    team_names = teams_df["team_name"].tolist()
    team_name = st.selectbox("Select Your Team", team_names)

    team = teams_df[teams_df["team_name"] == team_name].iloc[0]
    pin_required = str(team["team_pin"])

    entered_pin = st.text_input("Enter Team PIN", type="password")

    if entered_pin != pin_required:
        st.info("Enter correct Team PIN to continue")
        st.stop()

    st.success(f"Authenticated as {team_name}")
    st.markdown("---")

    # ---------- LOAD LIVE STATE ----------
    live = get_live()

    if live.get("status") != "LIVE":
        st.warning("No active bidding right now")
        st.stop()

    current_player = live.get("current_player_name")
    current_bid = int(live.get("current_bid", 0))
    leading_team = live.get("leading_team")

    # ---------- DISPLAY ----------
    st.subheader(f"🏏 {current_player}")
    st.markdown(f"**Current Bid:** ₹ {current_bid}")
    st.markdown(f"**Leading Team:** {leading_team or 'None'}")

    st.markdown("---")

    # ---------- BID ACTIONS ----------
    bid_increment = st.selectbox(
        "Bid Increment",
        [1, 2, 5, 10],
        index=1
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬆ Place Bid"):
            new_bid = current_bid + bid_increment

            write_kv("Live_Auction", "current_bid", new_bid)
            write_kv("Live_Auction", "leading_team", team_name)
            write_kv("Live_Auction", "leading_team_color", team["team_color"])
            write_kv("Live_Auction", "last_action", "BID")

            bump_refresh_token(live)

            st.success(f"Bid placed: ₹ {new_bid}")

    with col2:
        if st.button("🚫 Pass"):
            # For now, just record action
            write_kv("Live_Auction", "last_action", f"PASS:{team_name}")
            bump_refresh_token(live)

            st.info("You passed on this bid")
