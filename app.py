import streamlit as st
import google.generativeai as genai

# --- 1. 核心配置 ---
# 使用 .get() 避免 secrets 完全不存在時觸發致命錯誤
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error("❌ 未偵測到 API Key。請在 Render 環境變數中設定 'GOOGLE_API_KEY'。")
        st.stop()
except Exception:
    st.error("⚠️ 無法讀取 Secrets。請確認 Render 的 Environment 已經設定好 GOOGLE_API_KEY。")
    st.stop()

# 升級為 2026 最新型號
model = genai.GenerativeModel('gemini-3-flash-preview')

# --- 2. 核心邏輯：蔡台長審美演算法 ---
def generate_headline_decision(facts, insight, reference, style_level):
    system_prompt = f"""
    你是一位擁有 30 年經驗的電視新聞總編輯，負責 18 點新聞標題最後定案。
    你的最高準則是遵循『蔡台長』的審美：【不要為了平衡犧牲精彩度，但兩者必須並存】。

    【蔡台長觀點框架】：
    1. **拒絕文字遊戲**：禁止使用驚呆、火速、慘了、神速、竟然。
    2. **利益位移**：誰獲益？誰是沈默的輸家？
    3. **時機巧合**：為什麼是現在發生？是否在掩蓋其他醜聞？
    4. **雙向平衡**：標題必須同時包含兩造數據或對立點。

    【輸入內容】：
    - 原始事實數據：{facts}
    - 參考內文：{reference}
    - 製作人指令：{insight}
    - 風格等級：{style_level}

    【任務】：
    第一部分：產出三個標題方案（穩健型、權力觀點型、視覺張力型）。
    第二部分：從中選出一個最符合『蔡台長』要求、既平衡又精彩的【最優解】，並說明理由。
    """

    try:
        response = model.generate_content(
            system_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3)
        )
        return response.text
    except Exception as e:
        return f"❌ 系統錯誤：{str(e)}"

# --- 3. UI 介面設定 ---
st.set_page_config(page_title="NVE v28.0 - Professional", layout="wide")

# 初始化指令暫存
if "auto_insight" not in st.session_state:
    st.session_state.auto_insight = ""

st.title("📺 NewsVisionEngine v28.0")
st.subheader("製作人專業工作台：觀點導航與決策系統")
st.divider()

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.markdown("#### 📥 編輯台輸入")
    
    # 1. 原始事實數據
    facts_input = st.text_area(
        "1. 原始事實數據 (關鍵對比)", 
        placeholder="例如：川普30s/范斯5s，或預算100億/僅撥款2億", 
        height=80
    )
    
    st.divider()

    # 觀點導航按鈕
    st.markdown("##### 💡 觀點導航儀")
    tab1, tab2 = st.tabs(["🔥 核心攻防", "🌐 深度透視"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 找邏輯矛盾"):
                st.session_state.auto_insight = "分析此事實中，言行或數據最不一致的地方，找出不合理的轉折點。"
        with c2:
            if st.button("💰 追利益獲取"):
                st.session_state.auto_insight = "誰是這件事背後的資源獲取者？他們付出了什麼代價？誰是沈默輸家？"
    
    with tab2:
        c3, c4 = st.columns(2)
        with c3:
            if st.button("🔄 政策回力鏢"):
                st.session_state.auto_insight = "比對過去立場，指出今日行動是否為『髮夾彎』，其政治代價為何？"
        with c4:
            if st.button("🎭 拆解風向球"):
                st.session_state.auto_insight = "判斷此訊息是否為測試輿論的『風向球』？目的為何？誰在放話？"

    # 2. 製作人指令
    insight_input = st.text_area(
        "2. 蔡台長/慧娟姐重點指令", 
        value=st.session_state.auto_insight, 
        height=80
    )
    
    # 3. 風格選擇
    style_choice = st.select_slider(
        "3. 風格傾向",
        options=["極致專業", "平衡聚焦", "搶眼精彩"],
        value="平衡聚焦"
    )

    st.divider()

    # 4. 參考內文 (放在左側欄位最下面)
    reference_input = st.text_area(
        "4. 參考內文 (新聞稿/通訊社內容)", 
        placeholder="在此貼入長篇稿件，AI 會自動進行比對與提煉...", 
        height=200
    )
    
    go_btn = st.button("🚀 開始深度產出", use_container_width=True)

with col_out:
    st.markdown("#### 🚀 決策建議方案")
    if go_btn:
        if facts_input or reference_input:
            with st.spinner("正在依照蔡台長審美進行篩選..."):
                final_result = generate_headline_decision(
                    facts_input, insight_input, reference_input, style_choice
                )
                st.markdown(final_result)
        else:
            st.warning("製作人，請至少輸入事實數據或參考內文喔！")

st.divider()
st.caption("2026.04 Digital Transformation | 蔡台長標題決策邏輯已載入 | Model: Gemini-3-Flash")
