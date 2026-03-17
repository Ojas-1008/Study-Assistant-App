import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Header Section
st.title("Smart Study Assistant 📚")
st.subheader("An AI-powered NLP web app to help you study effectively.")