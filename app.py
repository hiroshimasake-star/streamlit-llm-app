from dotenv import load_dotenv

load_dotenv()

import os

import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage



# -----------------------------
# 0) .env を読み込む（OPENAI_API_KEY）
# -----------------------------
load_dotenv()


# -----------------------------
# 1) ④：入力テキスト と 選択値 を受け取り、回答（文字列）を返す関数
# -----------------------------
def ask_llm(input_text: str, expert_type: str) -> str:
    """
    引数:
      input_text: ユーザー入力テキスト
      expert_type: ラジオボタンの選択値（例: "日本酒ソムリエ", "酒屋の販売スタッフ"）
    戻り値:
      LLMの回答（文字列）
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "エラー：OPENAI_API_KEY が見つかりません。.env に設定されているか確認してください。"

    # ③：専門家ごとの system message を切り替える
    system_messages = {
        "日本酒ソムリエ": (
            "あなたは日本酒ソムリエです。"
            "味わい（甘口/辛口）、香り、製法、温度帯（冷酒/常温/燗）、料理との相性を踏まえて、"
            "専門的かつ分かりやすく丁寧に解説してください。"
            "専門用語を使う場合は、短く補足して初心者にも伝わるようにしてください。"
        ),
        "酒屋の販売スタッフ": (
            "あなたは酒屋の販売スタッフです。"
            "贈り物・ご自宅用・初心者向けなど用途を重視し、難しい専門用語は避けて、"
            "お客様が選びやすいように丁寧に提案してください。"
            "必要があれば質問を1〜2個だけ返して、好みや用途の確認も行ってください。"
        ),
    }

    system_text = system_messages.get(expert_type, system_messages["酒屋の販売スタッフ"])

    # ②：LangChain（Chat models）で LLM に渡す messages を作る
    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=input_text),
    ]

    # Lesson8準拠：ChatOpenAI を使う
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3)

    try:
        # なるべく新しい書き方（deprecated回避）
        result = llm.invoke(messages)
        return result.content
    except Exception as e:
        return f"エラー：LLMの呼び出しに失敗しました。詳細: {e}"


# -----------------------------
# 2) ⑤：アプリの説明（画面表示）
# -----------------------------
st.set_page_config(page_title="サケストア｜日本酒相談AI（デモ）", page_icon="🍶")
st.title("サケストア｜日本酒相談AI（デモ）")

st.write(
    "当アプリは、日本酒に関するご相談に対して、AIが**専門家の視点**からご案内する試作アプリです。  \n"
    "用途やお好みに応じて、異なる立場の専門家をお選びいただけます。"
)

with st.expander("ご利用方法 / 専門家の違い（クリックで開く）", expanded=True):
    st.markdown(
        """
**ご利用方法**
1. 回答してほしい専門家を選択してください  
2. ご相談内容を入力してください  
3. 送信すると、選択した専門家の視点で回答します  

**専門家のご紹介**
- **日本酒ソムリエ**：味わい・香り・製法・温度帯・料理との相性など、特徴を専門的かつ分かりやすく解説します。  
- **酒屋の販売スタッフ**：贈り物やご自宅用など用途を重視し、日本酒に詳しくない方にも選びやすいご提案を行います。  

**入力例**
- 日本酒初心者でも飲みやすいものを教えてほしい  
- 父の誕生日プレゼントに合う日本酒は？  
- 刺身に合う日本酒を探しています  
"""
    )

# -----------------------------
# 3) ③：専門家選択（ラジオボタン）
# -----------------------------
expert_type = st.radio(
    "専門家を選択してください",
    ["日本酒ソムリエ", "酒屋の販売スタッフ"],
    horizontal=True,
)

# -----------------------------
# 4) ②：入力フォーム（テキスト）→ 送信 → 回答表示
# -----------------------------
input_text = st.text_area(
    "ご相談内容を入力してください",
    placeholder="例：フルーティで飲みやすい日本酒を探しています。おすすめは？",
    height=140,
)

col1, col2 = st.columns([1, 3])
with col1:
    send = st.button("送信", type="primary")

with col2:
    st.caption("※ 本アプリはデモ用途のため、回答内容は参考情報です。未成年者の飲酒は法律で禁止されています。")

if send:
    if not input_text.strip():
        st.warning("ご相談内容を入力してください。")
    else:
        with st.spinner("回答を作成しています…"):
            answer = ask_llm(input_text=input_text, expert_type=expert_type)

        st.subheader("回答")
        st.write(answer)
