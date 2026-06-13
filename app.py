import streamlit as st
from google import genai
from PIL import Image

# 1. ページ全体の初期設定
st.set_page_config(layout="wide", page_title="LINE Global Localization Assistant")

# APIキーの設定（Streamlitのシークレット機能を使って隠す）
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# LINEグリーンのカスタムCSSを注入
st.markdown("""
    <style>
        .main-header { background-color: #00C300; color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
        .stButton>button { background-color: #00C300 !important; color: white !important; font-weight: bold !important; width: 100%; border: none !important; padding: 12px !important; border-radius: 8px !important; }
        .stButton>button:hover { background-color: #009900 !important; }
    </style>
""", unsafe_allow_html=True)

# ヘッダーエリア
st.markdown('<div class="main-header"><h1>🌍 LINE Global Localization Assistant</h1></div>', unsafe_allow_html=True)

# 2. 2カラム構成の作成 (左：日本語入力、右：翻訳出力)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 日本語の基本設定")
    
    base_title = st.text_input("1. スタンプのタイトル（日本語）", placeholder="例：毎日使える！元気なシーサーちゃん")
    base_desc = st.text_area("2. スタンプの説明文（日本語）", placeholder="例：日常会話で使いやすい、表情豊かなシーサーのスタンプです。お友達や家族とのトークにどうぞ！")
    
    ref_image = st.file_uploader("3. パッケージのメイン画像（任意：AIにニュアンスを伝えるため）", type=["png", "jpg", "jpeg"])
    if ref_image:
        st.image(ref_image, caption="読み込んだ画像", width=150)

    generate_btn = st.button("🌐 多言語メタデータを一括生成")

with col2:
    st.subheader("📋 ローカライズ結果（コピー用）")
    
    if generate_btn:
        if not base_title or not base_desc:
            st.error("タイトルと説明文を入力してください！")
        else:
            try:
                with st.spinner("⏳ 各国のチャット文化に合わせてローカライズ中..."):
                    # 絵文字禁止のルールを【厳守する条件】に強く追加
                    prompt_text = f"""
                    以下のLINEスタンプのタイトルと説明文を、5つの地域向けに最適なニュアンスで翻訳・ローカライズしてください。
                    【対象地域】アメリカ（英語）、台湾（繁体字）、インドネシア（インドネシア語）、タイ（タイ語）、韓国（韓国語）

                    【元の日本語】
                    タイトル：{base_title}
                    説明文：{base_desc}

                    【厳守する条件】
                    1. 文字数制限：タイトルは40文字以内、説明文は160文字以内に必ず収めること。
                    2. 絵文字・特殊記号の禁止：タイトルおよび説明文には、絵文字（Emoji）や環境依存文字を絶対に含めないこと。すべてプレーンなテキストのみで記述してください。
                    3. 表現：直訳ではなく、各地域のメッセンジャーアプリで好まれる、自然でキャッチーな言い回しにすること。
                    4. 出力形式：登録作業でコピー＆ペーストしやすいよう、以下のフォーマットに完全に従い、タイトルと説明文の間には必ず改行（空行）を入れること。

                    【出力フォーマット】
                    ### 🇺🇸 アメリカ（英語）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)

                    ---
                    (以下、他の言語も同じフォーマットで出力)
                    """
                    
                    contents_to_send = [prompt_text]
                    
                    if ref_image:
                        img = Image.open(ref_image)
                        contents_to_send.append("※この画像はスタンプの実際の雰囲気です。翻訳のテンションの参考にしてください。")
                        contents_to_send.append(img)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_to_send
                    )
                    
                    st.success("🎉 ローカライズが完了しました！")
                    st.write("各言語のテキストをダブルクリックしてコピーし、登録画面に貼り付けてください。")
                    
                    st.markdown(response.text)
                        
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.info("日本語のタイトルと説明文を入力してボタンを押すと、各国のストア向けのテキストが一瞬で生成されます。")