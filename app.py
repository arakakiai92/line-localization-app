import streamlit as st
from google import genai
from PIL import Image
import re

# 1. ページ全体の初期設定
st.set_page_config(layout="wide", page_title="LINE Global Localization Assistant")

# APIキーの設定（Streamlitのシークレット機能）
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
                    # プロンプト（出力フォーマットをより厳格に固定し、パースしやすくしました）
                    prompt_text = f"""
                    以下のLINEスタンプのタイトルと説明文を、5つの地域向けに最適なニュアンスで翻訳・ローカライズしてください。
                    【対象地域】アメリカ（英語）、台湾（繁体字）、インドネシア（インドネシア語）、タイ（タイ語）、韓国（韓国語）

                    【元の日本語】
                    タイトル：{base_title}
                    説明文：{base_desc}

                    【厳守する条件】
                    1. 文字数制限：タイトルは40文字以内、説明文は160文字以内に必ず収めること。（特に英語やインドネシア語などは文字数が多くなりがちなので、簡潔な表現を選ぶこと）
                    2. 絵文字・特殊記号の禁止：タイトルおよび説明文には、絵文字（Emoji）や環境依存文字を絶対に含めないこと。
                    3. 表現：直訳ではなく、各地域のメッセンジャーアプリで好まれる、自然でキャッチーな言い回しにすること。
                    4. 出力形式：以下のフォーマットに完全に従うこと。

                    【出力フォーマット】
                    ### 🇺🇸 アメリカ（英語）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)

                    ---
                    ### 🇹🇼 台湾（繁体字）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)

                    ---
                    ### 🇮🇩 インドネシア（インドネシア語）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)

                    ---
                    ### 🇹🇭 タイ（タイ語）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)

                    ---
                    ### 🇰🇷 韓国（韓国語）
                    **タイトル:** (ここにタイトルを出力)

                    **説明文:** (ここに説明文を出力)
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
                    
                    result_text = response.text
                    
                    # --- 📏 ここから：文字数カウントと判定のロジック ---
                    st.subheader("📏 文字数チェック（自動判定）")
                    
                    # 生成されたテキストから、正規表現を使ってタイトルと説明文を抽出
                    regions = re.findall(r'###\s*(.*)', result_text)
                    titles = re.findall(r'\*\*タイトル:\*\*\s*(.*)', result_text)
                    descs = re.findall(r'\*\*説明文:\*\*\s*(.*)', result_text)
                    
                    has_error = False
                    
                    if len(regions) > 0 and len(regions) == len(titles) and len(regions) == len(descs):
                        # 各言語ごとに文字数をカウント
                        for i in range(len(regions)):
                            region_name = regions[i].strip()
                            title_len = len(titles[i].strip())
                            desc_len = len(descs[i].strip())
                            
                            # LINEの制限（タイトル40、説明文160）で判定
                            title_status = "✅" if title_len <= 40 else "❌"
                            desc_status = "✅" if desc_len <= 160 else "❌"
                            
                            st.write(f"**{region_name}** | タイトル: {title_len}/40文字 {title_status} | 説明文: {desc_len}/160文字 {desc_status}")
                            
                            # 1つでもオーバーしていればエラーフラグを立てる
                            if title_len > 40 or desc_len > 160:
                                has_error = True
                    else:
                        st.warning("文字数の自動計算に失敗しましたが、テキストの生成自体は完了しています。")

                    # 判定結果に応じてメッセージと表示を切り替え
                    if has_error:
                        st.error("⚠️ 文字数制限（タイトル40文字 / 説明文160文字）をオーバーしている言語があります。もう一度「多言語メタデータを一括生成」ボタンを押して再生成してください。")
                    else:
                        st.success("🎉 すべての言語が文字数制限内に収まっています！以下のテキストをコピーして登録画面に貼り付けてください。")
                    
                    # 最後に生成されたテキスト全文を表示
                    st.markdown(result_text)
                        
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.info("日本語のタイトルと説明文を入力してボタンを押すと、各国のストア向けのテキストが一瞬で生成されます。")
