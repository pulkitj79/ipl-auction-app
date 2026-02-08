import streamlit as st
from sheets import read_sheet

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


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
    st.session_state.last_bid_team_color = "#f5c518"
    st.session_state.flash = False

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

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            f"""
            <div class="player-card">
                <div class="player-name">
                    {st.session_state.current_player['player_name']}
                </div>
                <div class="player-price">
                    Base Price: {st.session_state.current_player['base_price']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="bid-box">
                <div>Current Bid</div>
                <div class="current-bid">
                    ₹ {st.session_state.current_bid}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        team = st.selectbox(
            "Bidding Team",
            teams_df["team_name"].tolist()
        )

        if st.button("⬆️ PLACE BID"):
            st.session_state.current_team = team

            team_color = teams_df[
                teams_df["team_name"] == team
            ].iloc[0]["team_color"]
        
            st.session_state.last_bid_team_color = team_color
            st.session_state.current_bid += 2
            st.session_state.flash = True

        if st.button("🔨 SOLD"):
            st.markdown(
                f"""
                <div class="sold">
                    SOLD to {st.session_state.current_team} for ₹ {st.session_state.current_bid}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.session_state.bidding_active = False
