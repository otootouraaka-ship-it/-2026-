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

st.title("げんしけんにじさんじ共通テスト")

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

df["得点"] = scores

# =========================
# 統計量
# =========================

mean_score = df["得点"].mean()

std_score = df["得点"].std()

max_score = len(ANSWER_KEY)

accuracy = (
    df["得点"].sum()
    / (len(df) * max_score)
) * 100

# 偏差値
if std_score != 0:
    df["偏差値"] = (
        50 + 10 *
        (df["得点"] - mean_score)
        / std_score
    )
else:
    df["偏差値"] = 50

# ランキング
df["順位"] = (
    df["得点"]
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
    df["得点"],
    bins=range(max_score + 2),
)

ax.set_xlabel("得点")
ax.set_ylabel("人数")

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
    "問題番号": question_accuracy.keys(),
    "正答率": question_accuracy.values()
})

st.bar_chart(
    qa_df.set_index("問題")
)

# =========================
# ランキング表示
# =========================

st.subheader("ランキング")

# 表示用DataFrame
ranking_df = df[[
    "ハンドルネーム",
    "得点",
    "偏差値",
    "順位"
]].copy()

ranking_df = ranking_df.sort_values(
    by=["得点", "偏差値"],
    ascending=False
)

# rankを整数化
ranking_df["順位"] = ranking_df["順位"].astype(int)

# インデックス整理
ranking_df = ranking_df.reset_index(drop=True)

# =========================
# ページング設定
# =========================

ITEMS_PER_PAGE = 10

total_items = len(ranking_df)

total_pages = (
    total_items - 1
) // ITEMS_PER_PAGE + 1

# session_state初期化
if "page" not in st.session_state:
    st.session_state.page = 0

# =========================
# ページ切替ボタン
# =========================

col1, col2, col3 = st.columns([1,2,1])

with col1:
    if st.button("◀ 前へ"):

        if st.session_state.page > 0:
            st.session_state.page -= 1

with col3:
    if st.button("次へ ▶"):

        if st.session_state.page < total_pages - 1:
            st.session_state.page += 1

# =========================
# 現在ページ計算
# =========================

start_idx = (
    st.session_state.page
    * ITEMS_PER_PAGE
)

end_idx = start_idx + ITEMS_PER_PAGE

page_df = ranking_df.iloc[
    start_idx:end_idx
]

# =========================
# 表示
# =========================

st.write(
    f"ページ {st.session_state.page + 1} / {total_pages}"
)

st.dataframe(
    page_df,
    use_container_width=True
)
# =========================
# 生データ
# =========================

with st.expander("回答データ"):

    st.dataframe(df)
