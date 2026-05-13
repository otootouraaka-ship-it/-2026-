import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import gspread
from google.oauth2.service_account import Credentials

from streamlit_autorefresh import st_autorefresh

# =========================
# 自動更新
# =========================

st_autorefresh(interval=5000, key="refresh")

# =========================
# Streamlit設定
# =========================

st.set_page_config(
    page_title="リアルタイム試験集計",
    layout="wide"
)

st.title("リアルタイム試験集計システム")

# =========================
# Google Sheets接続
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)

# スプレッドシート名
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TOUV7U2uJMHM2DO08_Dqhd_babEl-XESRXKIfIqpiYE/edit?resourcekey=&gid=1281103730#gid=1281103730"

sheet = client.open_by_url(SHEET_URL).sheet1

data = sheet.get_all_records()

# =========================
# DataFrame化
# =========================

df = pd.DataFrame(data)

# =========================
# 正答設定
# =========================

ANSWER_KEY = {
    "Q1": "A",
    "Q2": "C",
    "Q3": "B",
    "Q4": "D",
    "Q5": "A"
}

# =========================
# 採点
# =========================

scores = []

for _, row in df.iterrows():

    score = 0

    for q, ans in ANSWER_KEY.items():

        if str(row[q]).strip() == ans:
            score += 1

    scores.append(score)

df["score"] = scores

# =========================
# 統計量
# =========================

mean_score = df["score"].mean()

std_score = df["score"].std()

max_score = len(ANSWER_KEY)

accuracy = (
    df["score"].sum()
    / (len(df) * max_score)
) * 100

# 偏差値
if std_score != 0:
    df["hensachi"] = (
        50 + 10 *
        (df["score"] - mean_score)
        / std_score
    )
else:
    df["hensachi"] = 50

# ランキング
df["rank"] = (
    df["score"]
    .rank(
        ascending=False,
        method="min"
    )
)

# =========================
# 上部メトリクス
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "回答人数",
    len(df)
)

col2.metric(
    "平均点",
    round(mean_score, 2)
)

col3.metric(
    "標準偏差",
    round(std_score, 2)
)

col4.metric(
    "正答率",
    f"{accuracy:.1f}%"
)

# =========================
# スコア分布
# =========================

st.subheader("得点分布")

fig, ax = plt.subplots()

ax.hist(
    df["score"],
    bins=range(max_score + 2),
)

ax.set_xlabel("Score")
ax.set_ylabel("Count")

st.pyplot(fig)

# =========================
# 問題別正答率
# =========================

st.subheader("問題別正答率")

question_accuracy = {}

for q, ans in ANSWER_KEY.items():

    correct = (
        df[q]
        .astype(str)
        .str.strip()
        == ans
    ).sum()

    rate = correct / len(df) * 100

    question_accuracy[q] = rate

qa_df = pd.DataFrame({
    "Question": question_accuracy.keys(),
    "Accuracy": question_accuracy.values()
})

st.bar_chart(
    qa_df.set_index("Question")
)

# =========================
# ランキング表示
# =========================

st.subheader("ランキング")

ranking_df = df[[
    "score",
    "hensachi",
    "rank"
]]

ranking_df = ranking_df.sort_values(
    by="rank"
)

st.dataframe(ranking_df)

# =========================
# 生データ
# =========================

with st.expander("回答データ"):

    st.dataframe(df)
