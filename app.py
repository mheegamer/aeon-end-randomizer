# ======================================================================
# Aeon's End Randomizer (Final Version - Fixed Display Game Function)
# ======================================================================

# ==============================================================================
# Aeon's End Randomizer - Final Version (Filter + New Local Storage Method)
# ==============================================================================

# --- 1. Import ไลบรารีที่จำเป็น ---
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import json
import base64 # ใช้ในการเข้ารหัสข้อมูลก่อนส่งให้ JavaScript
from streamlit_javascript import st_javascript # ไลบรารีใหม่

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


# --- 4. ส่วนของการเชื่อมต่อกับ Google Sheets ---
@st.cache_data(ttl=600)
def load_data_from_sheet(sheet_name):
    try:
        # สำหรับ Deploy ให้ใช้ st.secrets
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"])
    except Exception:
        # สำหรับรันบนเครื่องตัวเอง ให้ใช้ไฟล์ credentials.json
        try:
            scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        except Exception as e_local:
            st.sidebar.error("ไม่พบไฟล์ credentials.json")
            return pd.DataFrame()
            
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open("Aeon's End - Game Data")
        worksheet = spreadsheet.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        if 'Level' in df.columns:
            df['Level'] = pd.to_numeric(df['Level'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.sidebar.error(f"เกิดข้อผิดพลาดในการโหลดชีต '{sheet_name}'.")
        return pd.DataFrame()

# --- 5. โหลดข้อมูลและเตรียม State ---
with st.spinner('กำลังเชื่อมต่อกับ Google Sheets และโหลดข้อมูลการ์ด...'):
    df_mages_full = load_data_from_sheet("Mages")
    df_nemeses_full = load_data_from_sheet("Nemeses")
    df_cards_full = load_data_from_sheet("Cards")
    df_treasures_full = load_data_from_sheet("Treasures")

if "game_data" not in st.session_state:
    st.session_state.game_data = None

# --- 6. ฟังก์ชันสำหรับแสดงผล ---
def display_expedition(data):
    st.header(f"ผลการสุ่มสำหรับ: 🗺️ {data['mode']}")
    
    if st.button("💾 บันทึกเกมนี้ลงเบราว์เซอร์"):
        json_data = json.dumps(data)
        encoded_data = base64.b64encode(json_data.encode()).decode()
        st_javascript(f"localStorage.setItem('aeon_end_save', '{encoded_data}');")
        st.success("บันทึกข้อมูล Expedition ลงในเบราว์เซอร์นี้เรียบร้อยแล้ว!")
        st.toast("คุณสามารถปิดและเปิดหน้านี้ใหม่เพื่อโหลดเกมได้")
    
    tab_list = ["▶️ Setup & Battle 1", "⚔️ Battle 2", "⚔️ Battle 3", "👹 Battle 4 (Final)"]
    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

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
        st.subheader("💎 รางวัลจากด่านที่ 1 (เลือกรับจาก 3 ใบนี้)")
        cols = st.columns(3)
        for i, t in enumerate(data['treasures'][0]):
            with cols[i]:
                st.image(t['ImageURL'], width=200)
                st.caption(f"**{t['Name']}** (Level {t['Level']})<br>*{t['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
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
        st.subheader("💎 รางวัลจากด่านที่ 2 (เลือกรับจาก 3 ใบนี้)")
        cols = st.columns(3)
        for i, t in enumerate(data['treasures'][1]):
            with cols[i]:
                st.image(t['ImageURL'], width=200)
                st.caption(f"**{t['Name']}** (Level {t['Level']})<br>*{t['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
        cols = st.columns(3)
        for i, card in enumerate(data['replacements'][1]):
             with cols[i]:
                st.image(card['ImageURL'], width=200)
                st.caption(f"**{card['Name']}** (Cost: {card['Cost']})<br>*{card['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("👹 Battle 3: เผชิญหน้ากับ")
        nemesis_3 = data['nemeses'][2]
        st.title(nemesis_3['Name'])
        st.image(nemesis_3['ImageURL'], width=250)
        st.caption(f"*{nemesis_3['Expansion']}*")

    with tab4:
        st.subheader("💎 รางวัลจากด่านที่ 3 (เลือกรับจาก 3 ใบนี้)")
        cols = st.columns(3)
        for i, t in enumerate(data['treasures'][2]):
            with cols[i]:
                st.image(t['ImageURL'], width=200)
                st.caption(f"**{t['Name']}** (Level {t['Level']})<br>*{t['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
        cols = st.columns(3)
        for i, card in enumerate(data['replacements'][2]):
             with cols[i]:
                st.image(card['ImageURL'], width=200)
                st.caption(f"**{card['Name']}** (Cost: {card['Cost']})<br>*{card['Expansion']}*", unsafe_allow_html=True)
        st.divider()
        st.subheader("👹 Battle 4 (Final Boss): เผชิญหน้ากับ")
        nemesis_4 = data['nemeses'][3]
        st.title(nemesis_4['Name'])
        st.image(nemesis_4['ImageURL'], width=250)
        st.caption(f"*{nemesis_4['Expansion']}*")

def display_single_game(data):
    st.header(f"ผลการสุ่มสำหรับ: ⚔️ {data['mode']}")
    if st.button("💾 บันทึกเกมนี้ลงเบราว์เซอร์"):
        json_data = json.dumps(data)
        encoded_data = base64.b64encode(json_data.encode()).decode()
        st_javascript(f"localStorage.setItem('aeon_end_save', '{encoded_data}');")
        st.success("บันทึกข้อมูลเกมลงในเบราว์เซอร์นี้เรียบร้อยแล้ว!")

    nemesis = data['nemesis']
    mages = data['mages']
    market_cards = data['market']

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(nemesis['ImageURL'], width=250)
        st.caption(f"**{nemesis['Name']}**<br>*{nemesis['Expansion']}*", unsafe_allow_html=True)
    with col2:
        st.subheader("คุณจะต้องเผชิญหน้ากับ:")
        st.title(f"👹 {nemesis['Name']}")
    st.divider()

    st.subheader("เหล่าผู้วิเศษผู้ถูกเลือก (4 คน):")
    cols = st.columns(4)
    for i, mage in enumerate(mages):
        with cols[i]:
            st.image(mage['ImageURL'], width=200) 
            st.caption(f"**{mage['Name']}**<br>*{mage['Expansion']}*", unsafe_allow_html=True)
    st.divider()

    st.subheader("การ์ดในตลาด (Market):")
    for i in range(0, 9, 3):
        cols = st.columns(3) 
        row_cards = market_cards[i:i+3]
        for j in range(len(row_cards)):
            with cols[j]:
                card = row_cards[j]
                st.image(card['ImageURL'], width=200)
                st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})<br>*{card.get('Expansion', '')}*", unsafe_allow_html=True)

# --- 7. ส่วนควบคุมหลัก และ UI ---
st.title("🔮 Aeon's End Randomizer")
st.sidebar.header("⚙️ ตั้งค่าการสุ่ม")

# ฟิลเตอร์เลือกภาคเสริม
st.sidebar.subheader("เลือกภาคเสริมที่จะใช้")
if not df_cards_full.empty:
    expansions = pd.concat([df_mages_full['Expansion'], df_nemeses_full['Expansion'], df_cards_full['Expansion'], df_treasures_full['Expansion']]).dropna().unique().tolist()
    selected_expansions = []
    for expansion in sorted(expansions):
        if st.sidebar.checkbox(expansion, value=True):
            selected_expansions.append(expansion)
else:
    selected_expansions = []
    st.sidebar.warning("ไม่พบข้อมูลการ์ด")
st.sidebar.divider()

# เลือกโหมดเกม
game_mode = st.sidebar.selectbox("เลือกโหมดการเล่น", ["เล่นยาว (Expedition)", "เกมเดียว (Single Game)"])

# ปุ่มสุ่ม
if st.sidebar.button("🎲 เริ่มสุ่มใหม่!"):
    st.session_state.game_data = None 
    df_mages = df_mages_full[df_mages_full['Expansion'].isin(selected_expansions)]
    df_nemeses = df_nemeses_full[df_nemeses_full['Expansion'].isin(selected_expansions)]
    df_cards = df_cards_full[df_cards_full['Expansion'].isin(selected_expansions)]
    df_treasures = df_treasures_full[df_treasures_full['Expansion'].isin(selected_expansions)]
    
    try:
        if game_mode == "เล่นยาว (Expedition)":
            mages = df_mages.sample(4).to_dict('records')
            nemesis_1 = df_nemeses[df_nemeses['Level'] == 1].sample(1).iloc[0].to_dict()
            nemesis_2 = df_nemeses[df_nemeses['Level'] == 2].sample(1).iloc[0].to_dict()
            nemesis_3 = df_nemeses[df_nemeses['Level'] == 3].sample(1).iloc[0].to_dict()
            nemesis_4 = df_nemeses[df_nemeses['Level'] == 4].sample(1).iloc[0].to_dict()
            initial_market_df = pd.concat([df_cards[df_cards['Type'] == 'Gem'].sample(3), df_cards[df_cards['Type'] == 'Relic'].sample(2), df_cards[df_cards['Type'] == 'Spell'].sample(4)])
            available_cards = df_cards.drop(initial_market_df.index)
            st.session_state.game_data = {
                "mode": "เล่นยาว (Expedition)",
                "initial_market": initial_market_df.to_dict('records'), "mages": mages,
                "nemeses": [nemesis_1, nemesis_2, nemesis_3, nemesis_4],
                "replacements": [available_cards.sample(3).to_dict('records'), available_cards.drop(available_cards.sample(3).index).sample(3).to_dict('records'), available_cards.drop(available_cards.sample(6).index).sample(3).to_dict('records')],
                "treasures": [df_treasures[df_treasures['Level'] == 1].sample(3).to_dict('records'), df_treasures[df_treasures['Level'] == 2].sample(3).to_dict('records'), df_treasures[df_treasures['Level'] == 3].sample(3).to_dict('records')]
            }
        else: # Single Game
            st.session_state.game_data = {
                "mode": "เกมเดียว (Single Game)",
                "nemesis": df_nemeses.sample(1).to_dict('records')[0],
                "mages": df_mages.sample(4).to_dict('records'),
                "market": pd.concat([df_cards[df_cards['Type'] == 'Gem'].sample(3), df_cards[df_cards['Type'] == 'Relic'].sample(2), df_cards[df_cards['Type'] == 'Spell'].sample(4)]).to_dict('records')
            }
        st_javascript("localStorage.removeItem('aeon_end_save');")
        st.balloons()
    except Exception as e:
        st.error(f"การสุ่มล้มเหลว! อาจเป็นเพราะ Content จากภาคเสริมที่เลือกไว้มีไม่เพียงพอ: {e}")
        st.session_state.game_data = None

# --- ส่วนของการโหลดเกมจาก Local Storage ---
st.sidebar.divider()
st.sidebar.subheader("จัดการเกมที่บันทึกไว้")
saved_data_b64 = st_javascript("localStorage.getItem('aeon_end_save') || ''")

if saved_data_b64:
    if st.sidebar.button("⏮️ โหลดเกมล่าสุดจากเบราว์เซอร์"):
        try:
            decoded_str = base64.b64decode(saved_data_b64).decode()
            st.session_state.game_data = json.loads(decoded_str)
            st.toast("โหลดข้อมูลสำเร็จ!")
        except Exception as e:
            st.sidebar.error("ข้อมูลที่บันทึกไว้เสียหาย")
            st_javascript("localStorage.removeItem('aeon_end_save')")
    
    if st.sidebar.button("🗑️ ลบเกมที่บันทึกไว้"):
        st_javascript("localStorage.removeItem('aeon_end_save')")
        st.session_state.game_data = None
        st.toast("ลบข้อมูลที่บันทึกไว้แล้ว!")
        st.experimental_rerun()


# --- ส่วนแสดงผลหลัก ---
if st.session_state.game_data:
    display_game(st.session_state.game_data)
else:
    st.info("⬅️ กรุณาตั้งค่าการเล่นในเมนูด้านซ้าย แล้วกดปุ่ม 'เริ่มสุ่มใหม่!' หรือโหลดเกมที่บันทึกไว้")
# --- [เพิ่มฟังก์ชันนี้เพื่อแก้ไขปัญหา] ---
def display_game(game_data):
    if game_data['mode'] == "เล่นยาว (Expedition)":
        display_expedition(game_data)
    else:
        display_single_game(game_data)

# --- ส่วนแสดงผลหลัก ---
if st.session_state.game_data:
    display_game(st.session_state.game_data)
else:
    st.info("⬅️ กรุณาตั้งค่าการเล่นในเมนูด้านซ้าย แล้วกดปุ่ม 'เริ่มสุ่มใหม่!' หรือโหลดเกมที่บันทึกไว้")
