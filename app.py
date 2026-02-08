import streamlit as st
from sheets import read_sheet

st.set_page_config(
    page_title="IPL Auction",
    layout="wide"
)

st.title("🏏 IPL Style Auction – Live")

players_df = read_sheet("Players")
teams_df = read_sheet("Teams")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Players")
    st.dataframe(players_df)

with col2:
    st.subheader("Teams")
    st.dataframe(teams_df)

