import streamlit as st

from screens.projector import show_projector
from screens.auctioneer import show_auctioneer  # already inline earlier

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Auction System", layout="wide")

# -------------------------------------------------
# ROUTING
# -------------------------------------------------
screen = st.query_params.get("screen", "projector")

if screen == "projector":
    show_projector()

elif screen == "auctioneer":
    show_auctioneer()

else:
    st.title("Auction App")
    st.caption("Landing screen coming soon.")
