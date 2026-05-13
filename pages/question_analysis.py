import streamlit as st

# =========================
# 最優先
# =========================

st.set_page_config(
    page_title="問題分析",
    layout="wide"
)

# =========================
# import
# =========================

import pandas as pd
import matplotlib.pyplot as plt

import gspread

from google.oauth2.service_account import Credentials

from streamlit_autorefresh import st_autorefresh

# =========================
# 自動更新
# =========================

st_autorefresh(
    interval=5000,
    key="analysis_refresh"
)

st.title("問題別選択率")

# =========================
# Sheets
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1TOUV7U2uJMHM2DO08_Dqhd_babEl-XESRXKIfIqpiYE/edit?resourcekey=&gid=1281103730#gid=1281103730"

sheet = client.open_by_url(
    SHEET_URL
).sheet1

data = sheet.get_all_records()

df = pd.DataFrame(data)

QUESTIONS = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5"
]

if "question_page" not in st.session_state:
    st.session_state.question_page = 0

question_input = st.number_input(
    "問題番号",
    min_value=1,
    max_value=len(QUESTIONS),
    value=st.session_state.question_page + 1
)

st.session_state.question_page = (
    question_input - 1
)

col1, col2, col3 = st.columns([1,2,1])

with col1:

    if st.button("◀ 前の問題"):

        if st.session_state.question_page > 0:
            st.session_state.question_page -= 1

with col3:

    if st.button("次の問題 ▶"):

        if st.session_state.question_page < len(QUESTIONS)-1:
            st.session_state.question_page += 1

current_question = QUESTIONS[
    st.session_state.question_page
]

st.header(current_question)

counts = (
    df[current_question]
    .astype(str)
    .value_counts()
)

percentages = (
    counts / counts.sum()
) * 100

analysis_df = pd.DataFrame({
    "Choice": percentages.index,
    "Percentage": percentages.values
})

display_df = analysis_df.copy()

display_df["Percentage"] = (
    display_df["Percentage"]
    .round(1)
    .astype(str)
    + "%"
)

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True
)

fig, ax = plt.subplots()

fig.patch.set_alpha(0)

ax.set_facecolor((0,0,0,0))

bars = ax.bar(
    analysis_df["Choice"],
    analysis_df["Percentage"],
    alpha=0.3
)

ax.set_ylim(0, 100)

ax.set_ylabel("Selection Rate (%)")

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.1f}%",
        ha='center'
    )

st.pyplot(fig)