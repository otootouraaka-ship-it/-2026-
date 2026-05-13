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
    layout="wide"
)

st.title("test")