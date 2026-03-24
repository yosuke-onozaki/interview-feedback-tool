import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="一次面接レポート自動生成ツール",
    page_icon="📝",
    layout="wide"
)

st.title("一次面接レポート自動生成ツール")

st.markdown("### 入力項目")

summary = st.text_input("◆一次面接官総評（手入力）")

interview_record = st.text_area(
    "◆面接記録（コピペ）",
    height=250,
    placeholder="面接時のやり取り、印象、発言内容などを貼り付けてください。"
)

record_url = st.text_input(
    "◆面接記録URL",
    placeholder="https://docs.google.com/document/d/..."
)

st.markdown("### 適性検査結果")

col1, col2, col3, col4 = st.columns(4)

with col1:
    g = st.number_input("知的(G)", min_value=0, max_value=200, value=0, step=1)

with col2:
    v = st.number_input("言語(V)", min_value=0, max_value=200, value=0, step=1)

with col3:
    n = st.number_input("数理(N)", min_value=0, max_value=200, value=0, step=1)

with col4:
    q = st.number_input("書記(Q)", min_value=0, max_value=200, value=0, step=1)

st.markdown("---")

if st.button("AIでレポート生成", use_container_width=True):
    missing_fields = []

    if not summary.strip():
        missing_fields.append("一次面接官総評")
    if not interview_record.strip():
        missing_fields.append("面接記録")
    if not record_url.strip():
        missing_fields.append("面接記録URL")

    if missing_fields:
        st.warning(f"次の項目を入力してください：{', '.join(missing_fields)}")
    else:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            client = OpenAI(api_key=api_key)

            prompt = f"""
あなたは在宅医療クリニックの採用責任者・人事責任者です。
以下の情報をもとに、実務でそのまま利用できる一次面接レポートを日本語で作成してください。

【前提】
- 出力は採用関係者向けの社内レポートです
- 文体は簡潔・実務的・読みやすいものにしてください
- 過度に断定せず、評価として自然な表現にしてください
- 面接記録の内容を踏まえつつ、実務上の判断材料になるよう整理してください
- 適性検査結果は、点数をそのまま並べるだけでなく、強み・弱み・業務上の示唆まで文章化してください
- AI分析では、面接記録と適性検査結果を掛け合わせ、配属適性・初期育成の観点まで踏み込んでください
- 出力は以下の見出し・順番を厳守してください
- 面接官所感は300字程度でまとめてください
- 適性検査結果は、画像のような実務文体に近い形で、数値→特徴→業務適性→総合所見の流れで整理してください
- AI分析は、面接記録と検査結果の整合・補完関係がわかるようにしてください
- 最後の「◆面接記録：」には、必ず入力されたURLだけをそのまま記載してください

【入力情報】
◆一次面接官総評
{summary}

◆面接記録
{interview_record}

◆面接記録URL
{record_url}

◆適性検査結果
知的(G): {g}
言語(V): {v}
数理(N): {n}
書記(Q): {q}

【出力フォーマット】
◆一次面接官総評：
{summary}

◆面接官所感：
（面接記録を300字程度で要約し、評価コメントとして自然に再構成する）

◆適性検査結果：
（以下の流れで自然な文章にする）
- まず点数を「知的(G)：xx点／言語(V)：xx点／数理(N)：xx点／書記(Q)：xx点」のように記載
- 次に、各指標から見える特徴を整理
- 次に、業務適性や強み・留意点を実務目線で記載
- 最後に総合所見をまとめる

◆AI分析（面接記録×適性検査結果）：
（面接で見られた人物像と検査結果を掛け合わせ、診療パートナー等の実務適性、初期配属、育成時のフォロー観点まで含めてまとめる）

◆面接記録：
{record_url}

【禁止事項】
- 見出しを変えない
- 箇条書きにしない
- 面接記録URLを省略しない
- 「AIとして」などの説明を入れない
"""

            with st.spinner("AIがレポートを生成中です..."):
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=prompt
                )

            result = response.output_text

            st.success("レポートを生成しました。")

            st.markdown("### 生成結果")
            st.text_area(
                "以下をコピーして利用できます",
                value=result,
                height=700
            )

        except KeyError:
            st.error("APIキーが見つかりません。.streamlit/secrets.toml の設定を確認してください。")
        except Exception as e:
            st.error(f"エラーが発生しました：{e}")
