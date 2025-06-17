# ==============================================================================
# Aeon's End Randomizer - Final Version (Local Storage + Filter + Deploy Ready)
# ==============================================================================

# --- 1. Import ไลบรารีที่จำเป็น ---
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import json
from streamlit_localstorage import get, set

# --- 2. ตั้งค่าหน้าเว็บหลัก ---
st.set_page_config(
    page_title="Aeon's End Randomizer",
    page_icon="👹",
    layout="wide"
)

# --- 3. CSS สำหรับปรับ Layout ---
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 1rem; }
        [data-testid="stVerticalBlock"] { gap: 0.75rem; }
        [data-testid="stHorizontalBlock"] { gap: 0.25rem; }
    </style>
""", unsafe_allow_html=True)


# --- 4. ส่วนของการเชื่อมต่อกับ Google Sheets (สำหรับ Deploy) ---
@st.cache_data(ttl=600)
def load_data_from_sheet(sheet_name):
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("Aeon's End - Game Data")
        worksheet = spreadsheet.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        if 'Level' in df.columns:
            df['Level'] = pd.to_numeric(df['Level'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.sidebar.error("เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets")
        st.sidebar.error("โปรดตรวจสอบว่าได้ตั้งค่า Secrets ถูกต้องแล้ว")
        print(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 5. โหลดข้อมูลและเตรียม State ---
with st.spinner('กำลังเชื่อมต่อกับ Google Sheets และโหลดข้อมูลการ์ด...'):
    df_mages_full = load_data_from_sheet("Mages")
    df_nemeses_full = load_data_from_sheet("Nemeses")
    df_cards_full = load_data_from_sheet("Cards")
    df_treasures_full = load_data_from_sheet("Treasures")

if "expedition_data" not in st.session_state:
    st.session_state.expedition_data = None


# --- 6. ฟังก์ชันสำหรับแสดงผล Expedition ---
def display_expedition(data):
    st.header(f"ผลการสุ่มสำหรับ: 🗺️ {data['mode']}")
    
    if st.button("💾 บันทึกเกมนี้ลงเบราว์เซอร์"):
        try:
            json_data = json.dumps(data)
            set("aeon_end_save", json_data)
            st.success("บันทึกข้อมูล Expedition ลงในเบราว์เซอร์นี้เรียบร้อยแล้ว!")
            st.toast("คุณสามารถปิดและเปิดหน้านี้ใหม่เพื่อโหลดเกมได้")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")
    
    tab_list = ["▶️ Setup & Battle 1", "⚔️ Battle 2", "⚔️ Battle 3", "👹 Battle 4 (Final)"]
    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

    # (โค้ดแสดงผลในแต่ละแท็บเหมือนเดิม)
    with tab1:
        st.subheader("🛒 ตลาดเริ่มต้น (Initial Market)")
        market_cards = data['initial_market']
        for i in range(0, 9, 3):
            cols = st.columns(3) 
            row_cards = market_cards[i:i+3]
            for j in range(len(row_cards)):
                with cols[j]:
                    card = row_cards[j]
                    st.image(card['ImageURL'], width=200)
                    st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})<br>*{card.get('Expansion', '')}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("👥 กลุ่ม Mage สำหรับเริ่มต้น (เลือก 4 คน)")
        cols = st.columns(4)
        for i, mage in enumerate(data['mages']):
            with cols[i]:
                st.image(mage['ImageURL'], width=200)
                st.caption(f"**{mage['Name']}**<br>*{mage['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("👹 Battle 1: เผชิญหน้ากับ")
        nemesis_1 = data['nemeses'][0]
        st.title(nemesis_1['Name'])
        st.image(nemesis_1['ImageURL'], width=250)
        st.caption(f"*{nemesis_1['Expansion']}*")
    
    with tab2:
        st.subheader("💎 รางวัลจากด่านที่ 1")
        cols = st.columns(3)
        for i, t in enumerate(data['treasures'][0]):
            with cols[i]:
                st.image(t['ImageURL'], width=200)
                st.caption(f"**{t['Name']}** (Level {t['Level']})<br>*{t['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ")
        cols = st.columns(3)
        for i, card in enumerate(data['replacements'][0]):
                with cols[i]:
                st.image(card['ImageURL'], width=200)
                st.caption(f"**{card['Name']}** (Cost: {card['Cost']})<br>*{card['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("👹 Battle 2: เผชิญหน้ากับ")
        nemesis_2 = data['nemeses'][1]
        st.title(nemesis_2['Name'])
        st.image(nemesis_2['ImageURL'], width=250)
        st.caption(f"*{nemesis_2['Expansion']}*")
    
    with tab3:
        #... (โค้ดแสดงผล tab 3)
    with tab4:
        #... (โค้ดแสดงผล tab 4)

# --- 7. ส่วนควบคุมหลัก และ UI ---
st.title("🔮 Aeon's End Randomizer")
st.sidebar.header("⚙️ ตั้งค่าการสุ่ม")

# (โค้ดส่วน UI ที่เหลือเหมือนเดิมทั้งหมด)
# ...

# --- ส่วนของการโหลดเกมจาก Local Storage ---
st.sidebar.divider()
saved_data_json = get("aeon_end_save")
if saved_data_json:
    if st.sidebar.button("⏮️ โหลดเกมล่าสุดจากเบราว์เซอร์"):
        try:
            st.session_state.expedition_data = json.loads(saved_data_json)
            st.toast("โหลดข้อมูลสำเร็จ!")
        except Exception as e:
            st.sidebar.error("ข้อมูลที่บันทึกไว้เสียหาย")
            set("aeon_end_save", None) # ล้างข้อมูลที่เสียทิ้ง

# --- ส่วนแสดงผลหลัก ---
if st.session_state.expedition_data:
    display_expedition(st.session_state.expedition_data)
else:
    st.info("⬅️ กรุณาตั้งค่าการเล่นในเมนูด้านซ้าย แล้วกดปุ่ม 'เริ่มสุ่มใหม่!' หรือโหลดเกมที่บันทึกไว้")
