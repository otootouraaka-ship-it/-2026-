import streamlit as st

# =========================
# 最優先
# =========================

st.set_page_config(
    page_title="げんしけんにじさんじ共通テスト2026 in 清陵祭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# import
# =========================

import pandas as pd
import matplotlib.pyplot as plt
import base64

import gspread

from google.oauth2.service_account import Credentials

from streamlit_autorefresh import st_autorefresh

# =========================
# 自動更新
# =========================

st_autorefresh(
    interval=5000,
    key="refresh"
)

# =========================
# 背景
# =========================

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
            url("data:image/png;base64,{encoded}");

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

# =========================
# タイトル
# =========================

st.title(
    "げんしけんにじさんじ共通テスト2026 in 清陵祭"
)

# =========================
# Google Sheets
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

# =========================
# 問題設定
# =========================

ANSWER_KEY = {
    "Q1": {
        "answer": "A",
        "point": 5
    },
    "Q2": {
        "answer": "C",
        "point": 20
    },
    "Q3": {
        "answer": "B",
        "point": 10
    },
    "Q4": {
        "answer": "D",
        "point": 15
    },
    "Q5": {
        "answer": "A",
        "point": 50
    }
}

# =========================
# 採点
# =========================

scores = []

for _, row in df.iterrows():

    score = 0

    for q, setting in ANSWER_KEY.items():

        correct = setting["answer"]

        point = setting["point"]

        if str(row[q]).strip() == correct:
            score += point

    scores.append(score)

df["score"] = scores

# =========================
# 統計
# =========================

mean_score = df["score"].mean()

std_score = df["score"].std()

max_score = sum(
    x["point"]
    for x in ANSWER_KEY.values()
)

accuracy = (
    df["score"].sum()
    / (len(df) * max_score)
) * 100

# 偏差値

if std_score != 0:

    df["hensachi"] = (
        50
        + 10 *
        (df["score"] - mean_score)
        / std_score
    )

else:

    df["hensachi"] = 50

# 順位

df["rank"] = (
    df["score"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
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
# 得点分布
# =========================

st.subheader("得点分布")

fig, ax = plt.subplots()

fig.patch.set_alpha(0)

ax.set_facecolor((0,0,0,0))

ax.hist(
    df["score"],
    bins=range(max_score + 2),
    alpha=0.3
)

ax.set_xlabel("Score")

ax.set_ylabel("Count")

st.pyplot(fig)

# =========================
# 問題別正答率
# =========================

st.subheader("問題別正答率")

question_accuracy = {}

for q, setting in ANSWER_KEY.items():

    ans = setting["answer"]

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

fig, ax = plt.subplots()

fig.patch.set_alpha(0)

ax.set_facecolor((0,0,0,0))

bars = ax.bar(
    qa_df["Question"],
    qa_df["Accuracy"],
    alpha=0.3
)

ax.set_ylim(0, 100)

ax.set_ylabel("Accuracy (%)")

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.1f}%",
        ha='center'
    )

st.pyplot(fig)

# =========================
# ランキング
# =========================

st.subheader("ランキング")

ranking_df = df[[
    "ハンドルネーム",
    "score",
    "hensachi",
    "rank"
]].copy()

ranking_df = ranking_df.sort_values(
    by=["score", "hensachi"],
    ascending=False
)

ranking_df = ranking_df.reset_index(drop=True)

ranking_df = ranking_df[[
    "rank",
    "ハンドルネーム",
    "score",
    "hensachi"
]]

ranking_df.columns = [
    "順位",
    "名前",
    "得点",
    "偏差値"
]

ITEMS_PER_PAGE = 10

total_items = len(ranking_df)

total_pages = (
    total_items - 1
) // ITEMS_PER_PAGE + 1

if "page" not in st.session_state:
    st.session_state.page = 0

col1, col2, col3 = st.columns([1,2,1])

with col1:

    if st.button("◀ 前へ"):

        if st.session_state.page > 0:
            st.session_state.page -= 1

with col3:

    if st.button("次へ ▶"):

        if st.session_state.page < total_pages - 1:
            st.session_state.page += 1

start_idx = (
    st.session_state.page
    * ITEMS_PER_PAGE
)

end_idx = start_idx + ITEMS_PER_PAGE

page_df = ranking_df.iloc[
    start_idx:end_idx
]

st.write(
    f"ページ {st.session_state.page + 1} / {total_pages}"
)

st.dataframe(
    page_df,
    hide_index=True,
    use_container_width=True
)