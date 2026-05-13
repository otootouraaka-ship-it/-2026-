import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import base64

import gspread
from google.oauth2.service_account import Credentials

from streamlit_autorefresh import st_autorefresh

# =========================
# Streamlit設定
# =========================

st.set_page_config(
    page_title="げんしけんにじさんじ共通テスト2026 in 清陵祭",
    layout="wide",
    initial_sidebar_state="expanded"
)



def set_bg_image(image_file):

    with open(image_file, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    page_bg_img = f"""
    <style>
    
    .stApp {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.5),
                rgba(0,0,0,0.5)
            ),
            url("data:image/jpg;base64,{encoded}");
    
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    </style>
    """

    st.markdown(
        page_bg_img,
        unsafe_allow_html=True
    )

set_bg_image("image.png")

st.title("げんしけんにじさんじ共通テスト2026 in 清陵祭")
