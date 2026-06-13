import streamlit as st
from google import genai
from PIL import Image
import re

# 1. ページ全体の初期設定
st.set_page_config(layout="wide", page_title="LINE Global Localization Assistant")

# APIキーの設定
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# LINEグリーンのカスタムCSS
st.markdown("""
    <style>
        .main-header { background-color: #00C300; color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
        .stButton>button { background-color: #00C300 !important; color: white !important; font-weight: bold !important; width: 100%; border: none !important; padding: 12px !important; border-radius: 8px !important; }
        .stButton>button:hover { background-color: #009900 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🌍 LINE Global Localization Assistant</h1></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 日本語の基本設定")
    base_title = st.text_input("1. スタンプのタイトル（日本語）", placeholder="例：毎日使える！元気なシーサーちゃん")
    base_desc = st.text_area("2. スタンプの説明文（日本語）", placeholder="例：日常会話で使いやすい、表情豊かなシーサーのスタンプです。お友達や家族とのトークにどうぞ！")
    
    ref_image = st.file_uploader("3. パッケージのメイン画像（任意）", type=["png", "jpg", "jpeg"])
    if ref_image:
        st.image(ref_image, caption="読み込んだ画像", width=150)

    generate_btn = st.button("🌐 多言語メタデータを一括生成")

with col2:
    st.subheader("📋 ローカライズ結果（コピー用）")
    
    if generate_btn:
        if not base_title or not base_desc:
            st.error("タイトルと説明文を入力してください！")
        else:
            # 自動リトライの最大回数を設定
            max_retries = 3
            is_success = False
            final_result_text = ""
            
            # プログレスバーとステータス表示用
            status_text = st.empty()
            
            for attempt in range(max_retries):
                if is_success:
                    break
                    
                status_text.info(f"⏳ AIが翻訳中...（試行 {attempt + 1}/{max_retries} 回目: 文字数を自動調整しています）")
                
                try:
                    # 試行回数が増えるごとに、より強く「短くしろ」と命令を追加する
                    length_warning = ""
                    if attempt > 0:
                        length_warning = "【重要】前回の生成では文字数制限をオーバーしました。今回は必ず、各言語ともタイトルをさらに短く、説明文ももっと簡潔に削ってください。"

                    prompt_text = f"""
                    以下のLINEスタンプのタイトルと説明文を、5つの地域向けに翻訳・ローカライズしてください。
                    【対象地域】アメリカ（英語）、台湾（繁体字）、インドネシア（インドネシア語）、タイ（タイ語）、韓国（韓国語）

                    【元の日本語】
                    タイトル：{base_title}
                    説明文：{base_desc}

                    【厳守する条件】
                    1. 文字数制限：タイトルは40文字以内、説明文は160文字以内に【絶対に】収めること。
                    2. 絵文字・特殊記号の禁止：タイトルおよび説明文には、絵文字（Emoji）を絶対に含まないこと。
                    3. 表現：直訳ではなく、各地域のアプリで好まれる自然な言い回しにすること。
                    {length_warning}

                    【出力フォーマット】
                    ### 🇺🇸 アメリカ（英語）
                    **タイトル:** (タイトルを出力)

                    **説明文:** (説明文を出力)

                    ---
                    ### 🇹🇼 台湾（繁体字）
                    **タイトル:** (タイトルを出力)

                    **説明文:** (説明文を出力)

                    ---
                    ### 🇮🇩 インドネシア（インドネシア語）
                    **タイトル:** (タイトルを出力)

                    **説明文:** (説明文を出力)

                    ---
                    ### 🇹🇭 タイ（タイ語）
                    **タイトル:** (タイトルを出力)

                    **説明文:** (説明文を出力)

                    ---
                    ### 🇰🇷 韓国（韓国語）
                    **タイトル:** (タイトルを出力)

                    **説明文:** (説明文を出力)
                    """
                    
                    contents_to_send = [prompt_text]
                    if ref_image:
                        img = Image.open(ref_image)
                        contents_to_send.append(img)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_to_send
                    )
                    
                    result_text = response.text
                    
                    # Pythonによる厳密な文字数チェック
                    regions = re.findall(r'###\s*(.*)', result_text)
                    titles = re.findall(r'\*\*タイトル:\*\*\s*(.*)', result_text)
                    descs = re.findall(r'\*\*説明文:\*\*\s*(.*)', result_text)
                    
                    has_error = False
                    
                    if len(regions) > 0 and len(regions) == len(titles) and len(regions) == len(descs):
                        for i in range(len(regions)):
                            if len(titles[i].strip()) > 40 or len(descs[i].strip()) > 160:
                                has_error = True # 1つでもオーバーしたらエラー判定
                                break
                    else:
                        has_error = True # フォーマットが崩れた場合もやり直し
                    
                    # エラーがなければ成功としてループを抜ける
                    if not has_error:
                        is_success = True
                        final_result_text = result_text
                        
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    break
            
            # 全ての試行（ループ）が終わった後の画面表示
            status_text.empty() # ステータス文字を消す
            
            if is_success:
                st.success("🎉 文字数制限をクリアしました！以下のテキストをコピーして登録画面に貼り付けてください。")
                
                # 文字数確認用の表示
                with st.expander("文字数の確認"):
                    for i in range(len(regions)):
                        st.write(f"**{regions[i].strip()}** | タイトル: {len(titles[i].strip())}/40 | 説明文: {len(descs[i].strip())}/160")
                
                st.markdown(final_result_text)
            else:
                st.error("⚠️ 3回自動調整を試みましたが、文字数内に収めきれませんでした。元の日本語を少し短くして、再度お試しください。")
                if final_result_text:
                    st.markdown(final_result_text)
    else:
        st.info("日本語を入力してボタンを押すと、文字数制限を自動チェックしながら各国のストア向けテキストを生成します。")
