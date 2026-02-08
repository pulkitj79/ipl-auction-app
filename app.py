import streamlit as st
from sheets import read_sheet

st.set_page_config(
    page_title="IPL Auction",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "bidding_active" not in st.session_state:
    st.session_state.bidding_active = False
    st.session_state.current_player = None
    st.session_state.current_bid = 0
    st.session_state.current_team = None

# ------------------ LOAD DATA ------------------
players_df = read_sheet("Players")
teams_df = read_sheet("Teams")

st.title("🏏 IPL Style Player Auction")

# ------------------ SELECT PLAYER ------------------
unsold_players = players_df[players_df["status"] != "SOLD"]

st.subheader("Select Player")
player_name = st.selectbox(
    "Choose player to auction",
    unsold_players["player_name"].tolist()
)

selected_player = unsold_players[
    unsold_players["player_name"] == player_name
].iloc[0]

# ------------------ START AUCTION ------------------
if st.button("🚀 Start Auction"):
    st.session_state.bidding_active = True
    st.session_state.current_player = selected_player
    st.session_state.current_bid = selected_player["base_price"]
    st.session_state.current_team = None

# ------------------ AUCTION PANEL ------------------
if st.session_state.bidding_active:

    st.markdown("---")
    st.subheader("🔨 Live Auction")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"## {st.session_state.current_player['player_name']}")
        st.markdown(f"### Base Price: {st.session_state.current_player['base_price']}")
        st.markdown(f"## 💰 Current Bid: {st.session_state.current_bid}")

    with col2:
        team = st.selectbox(
            "Bidding Team",
            teams_df["team_name"].tolist()
        )

        if st.button("⬆️ Place Bid"):
            st.session_state.current_team = team
            st.session_state.current_bid += 2

        if st.button("🔨 SOLD"):
            st.success(
                f"SOLD to {st.session_state.current_team} for {st.session_state.current_bid}"
            )
            st.session_state.bidding_active = False
