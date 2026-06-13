import streamlit as st
from google import genai
from PIL import Image
import re

st.set_page_config(layout="wide", page_title="LINE Global Localization Assistant")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.markdown("""
    <style>
        .main-header { background-color: #00C300; color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
        .stButton>button { background-color: #00C300 !important; color: white !important; font-weight: bold !important; width: 100%; border: none !important; padding: 12px !important; border-radius: 8px !important; }
        .stButton>button:hover { background-color: #009900 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🌍 LINE Global Auto-Generator</h1></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 AI自動生成の設定")
    
    # 画像と、どんなテーマかだけを聞く
    ref_image = st.file_uploader("1. スタンプ画像（必須：AIが解析します）", type=["png", "jpg", "jpeg"])
    theme_keyword = st.text_input("2. パッケージのテーマや状況（例：風邪、毎日使える、丁寧語、シーサーの日常）", placeholder="例：インフルエンザ、風邪、体調不良")
    
    if ref_image:
        st.image(ref_image, caption="解析対象のスタンプ", width=150)

    generate_btn = st.button("🚀 AIにタイトル・説明文を自動作成させる")

with col2:
    st.subheader("📋 自動生成結果")
    
    if generate_btn:
        if not ref_image or not theme_keyword:
            st.error("スタンプ画像とテーマを入力してください！")
        else:
            max_retries = 3
            is_success = False
            final_result_text = ""
            status_text = st.empty()
            
            for attempt in range(max_retries):
                if is_success: break
                status_text.info(f"⏳ AIが画像からインスピレーションを受け、ローカライズ中...（試行 {attempt + 1}/3）")
                
                try:
                    img = Image.open(ref_image)
                    
                    # 完全に自動作成を指示
                    prompt_text = f"""
                    添付された画像を分析し、テーマ「{theme_keyword}」に基づいたLINEスタンプのタイトルと説明文を、5つの地域向けに最適化して生成してください。
                    【対象地域】アメリカ（英語）、台湾（繁体字）、インドネシア（インドネシア語）、タイ（タイ語）、韓国（韓国語）

                    【厳守条件】
                    1. 文字数：タイトルは40文字以内、説明文は160文字以内。
                    2. 絵文字禁止：絵文字や特殊記号は一切含めない。
                    3. 翻訳：直訳ではなく、各地域のメッセンジャーで自然に使われる口語で作成。

                    【出力フォーマット】
                    ### 🇺🇸 アメリカ（英語）
                    **タイトル:** **説明文:** ---
                    (以下、他の地域も同じフォーマットで出力)
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt_text, img]
                    )
                    
                    result_text = response.text
                    
                    # チェックロジック
                    regions = re.findall(r'###\s*(.*)', result_text)
                    titles = re.findall(r'\*\*タイトル:\*\*\s*(.*)', result_text)
                    descs = re.findall(r'\*\*説明文:\*\*\s*(.*)', result_text)
                    
                    has_error = False
                    if len(regions) > 0 and len(regions) == len(titles) and len(regions) == len(descs):
                        for i in range(len(regions)):
                            if len(titles[i].strip()) > 40 or len(descs[i].strip()) > 160:
                                has_error = True
                                break
                    else:
                        has_error = True
                    
                    if not has_error:
                        is_success = True
                        final_result_text = result_text
                        
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    break
            
            status_text.empty()
            if is_success:
                st.success("🎉 AIがパッケージのニュアンスを汲み取り、自動作成しました！")
                st.markdown(final_result_text)
            else:
                st.error("⚠️ AIの自動作成で文字数制限を突破できませんでした。画像が複雑すぎる可能性があります。")
    else:
        st.info("画像をアップロードし、簡単なテーマを入力するだけで、AIがすべて自動でライティングします。")
