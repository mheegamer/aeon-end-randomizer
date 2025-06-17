# ==============================================================================
# Aeon's End Randomizer - (ลบอนิเมชันลูกโป่ง)
# ==============================================================================

# --- 1. Import ไลบรารีที่จำเป็น ---
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random

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
YOUR_SHEET_NAME = "Aeon's End - Game Data"

@st.cache_data(ttl=600)
def load_data_from_sheet(sheet_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open(YOUR_SHEET_NAME)
        worksheet = spreadsheet.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        if 'Level' in df.columns:
            df['Level'] = pd.to_numeric(df['Level'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.sidebar.error(f"เกิดข้อผิดพลาดในการโหลดชีต '{sheet_name}'.")
        print(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 5. โหลดข้อมูลทั้งหมด ---
with st.spinner('กำลังเชื่อมต่อกับ Google Sheets และโหลดข้อมูลการ์ด...'):
    df_mages_full = load_data_from_sheet("Mages")
    df_nemeses_full = load_data_from_sheet("Nemeses")
    df_cards_full = load_data_from_sheet("Cards")
    df_treasures_full = load_data_from_sheet("Treasures")

# --- 6. ส่วนควบคุมใน Sidebar ---
st.title("🔮 Aeon's End Randomizer")
st.sidebar.header("⚙️ ตั้งค่าการสุ่ม")

st.sidebar.subheader("เลือกภาคเสริมที่จะใช้")
if not df_cards_full.empty:
    expansions = pd.concat([
        df_mages_full['Expansion'],
        df_nemeses_full['Expansion'],
        df_cards_full['Expansion'],
        df_treasures_full['Expansion']
    ]).dropna().unique().tolist()
    
    selected_expansions = []
    for expansion in sorted(expansions):
        if st.sidebar.checkbox(expansion, value=True):
            selected_expansions.append(expansion)
else:
    selected_expansions = []
    st.sidebar.warning("ไม่พบข้อมูลการ์ด")

st.sidebar.divider()

game_mode = st.sidebar.selectbox(
    "เลือกโหมดการเล่น",
    ["เล่นยาว (Expedition)", "เกมเดียว (Single Game)"]
)

if st.sidebar.button("🎲 เริ่มสุ่ม!"):
    # <<< ปรับแก้: ลบบรรทัด st.balloons() ออกไปจากตรงนี้ >>>
    
    # --- กรองข้อมูลตามภาคเสริมที่เลือก ---
    df_mages = df_mages_full[df_mages_full['Expansion'].isin(selected_expansions)]
    df_nemeses = df_nemeses_full[df_nemeses_full['Expansion'].isin(selected_expansions)]
    df_cards = df_cards_full[df_cards_full['Expansion'].isin(selected_expansions)]
    df_treasures = df_treasures_full[df_treasures_full['Expansion'].isin(selected_expansions)]
    
    # --- ตรรกะสำหรับโหมด "เล่นยาว (Expedition)" ---
    if game_mode == "เล่นยาว (Expedition)":
        st.header("ผลการสุ่มสำหรับ: 🗺️ เล่นยาว (Expedition)")
        try:
            # (โค้ดการสุ่มเหมือนเดิมทั้งหมด)
            mages = df_mages.sample(4)
            nemesis_1 = df_nemeses[df_nemeses['Level'] == 1].sample(1).iloc[0]
            nemesis_2 = df_nemeses[df_nemeses['Level'] == 2].sample(1).iloc[0]
            nemesis_3 = df_nemeses[df_nemeses['Level'] == 3].sample(1).iloc[0]
            nemesis_4 = df_nemeses[df_nemeses['Level'] == 4].sample(1).iloc[0]

            initial_gems = df_cards[df_cards['Type'] == 'Gem'].sample(3)
            initial_relics = df_cards[df_cards['Type'] == 'Relic'].sample(2)
            initial_spells = df_cards[df_cards['Type'] == 'Spell'].sample(4)
            initial_market_df = pd.concat([initial_gems, initial_relics, initial_spells])
            
            available_cards = df_cards.drop(initial_market_df.index)
            replacement_market_1 = available_cards.sample(3)
            available_cards = available_cards.drop(replacement_market_1.index)
            replacement_market_2 = available_cards.sample(3)
            available_cards = available_cards.drop(replacement_market_2.index)
            replacement_market_3 = available_cards.sample(3)
            
            treasures_1 = df_treasures[df_treasures['Level'] == 1].sample(3)
            treasures_2 = df_treasures[df_treasures['Level'] == 2].sample(3)
            treasures_3 = df_treasures[df_treasures['Level'] == 3].sample(3)
            
            tab_list = ["▶️ Setup & Battle 1", "⚔️ Battle 2", "⚔️ Battle 3", "👹 Battle 4 (Final)"]
            tab1, tab2, tab3, tab4 = st.tabs(tab_list)

            # (โค้ดแสดงผลเหมือนเดิมทั้งหมด)
            with tab1:
                st.subheader("🛒 ตลาดเริ่มต้น (Initial Market)")
                market_cards = initial_market_df.to_dict('records')
                for i in range(0, 9, 3):
                    cols = st.columns(3) 
                    row_cards = market_cards[i:i+3]
                    for j in range(len(row_cards)):
                        with cols[j]:
                            card = row_cards[j]
                            st.image(card['ImageURL'], width=200)
                            st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})")
                st.divider()
                st.subheader("👥 กลุ่ม Mage สำหรับเริ่มต้น (เลือก 4 คน)")
                cols = st.columns(4)
                for i, mage in enumerate(mages.itertuples()):
                    with cols[i]:
                        st.image(mage.ImageURL, width=200)
                        st.caption(f"**{mage.Name}**")
                st.divider()
                st.subheader("👹 Battle 1: เผชิญหน้ากับ")
                st.title(nemesis_1['Name'])
                st.image(nemesis_1['ImageURL'], width=250)
            
            with tab2:
                st.subheader("💎 รางวัลจากด่านที่ 1 (เลือกรับจาก 3 ใบนี้)")
                cols = st.columns(3)
                for i, t in enumerate(treasures_1.itertuples()):
                    with cols[i]:
                        st.image(t.ImageURL, width=200)
                        st.caption(f"**{t.Name}** (Level {t.Level})")
                st.divider()
                st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_1.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})")
                st.divider()
                st.subheader("👹 Battle 2: เผชิญหน้ากับ")
                st.title(nemesis_2['Name'])
                st.image(nemesis_2['ImageURL'], width=250)

            with tab3:
                st.subheader("💎 รางวัลจากด่านที่ 2 (เลือกรับจาก 3 ใบนี้)")
                cols = st.columns(3)
                for i, t in enumerate(treasures_2.itertuples()):
                    with cols[i]:
                        st.image(t.ImageURL, width=200)
                        st.caption(f"**{t.Name}** (Level {t.Level})")
                st.divider()
                st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_2.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})")
                st.divider()
                st.subheader("👹 Battle 3: เผชิญหน้ากับ")
                st.title(nemesis_3['Name'])
                st.image(nemesis_3['ImageURL'], width=250)

            with tab4:
                st.subheader("💎 รางวัลจากด่านที่ 3 (เลือกรับจาก 3 ใบนี้)")
                cols = st.columns(3)
                for i, t in enumerate(treasures_3.itertuples()):
                    with cols[i]:
                        st.image(t.ImageURL, width=200)
                        st.caption(f"**{t.Name}** (Level {t.Level})")
                st.divider()
                st.subheader("🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)")
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_3.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})")
                st.divider()
                st.subheader("👹 Battle 4 (Final Boss): เผชิญหน้ากับ")
                st.title(nemesis_4['Name'])
                st.image(nemesis_4['ImageURL'], width=250)

        except Exception as e:
            st.error("การสุ่มล้มเหลว! อาจเป็นเพราะ Content จากภาคเสริมที่เลือกไว้มีไม่เพียงพอ")
            st.error(f"รายละเอียด: {e}")

    # --- ตรรกะสำหรับโหมด "เกมเดียว (Single Game)" ---
    else: 
        st.header("ผลการสุ่มสำหรับ: ⚔️ เกมเดียว (Single Game)")
        try:
            nemesis = df_nemeses.sample(1).iloc[0]
            mages = df_mages.sample(4)
            
            gems = df_cards[df_cards['Type'] == 'Gem'].sample(3).to_dict('records')
            relics = df_cards[df_cards['Type'] == 'Relic'].sample(2).to_dict('records')
            spells = df_cards[df_cards['Type'] == 'Spell'].sample(4).to_dict('records')
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(nemesis['ImageURL'], caption=nemesis['Name'])
            with col2:
                st.subheader("คุณจะต้องเผชิญหน้ากับ:")
                st.title(f"👹 {nemesis['Name']}")
                st.info(f"มาจากภาคเสริม: {nemesis['Expansion']}")
            st.divider()

            st.subheader("เหล่าผู้วิเศษผู้ถูกเลือก (4 คน):")
            cols = st.columns(4)
            for i, mage in enumerate(mages.itertuples()):
                with cols[i]:
                    st.subheader(mage.Name)
                    st.image(mage.ImageURL, width=200) 
                    st.caption(f"ภาคเสริม: {mage.Expansion}")
            st.divider()

            st.subheader("การ์ดในตลาด (Market):")
            market_cards = gems + relics + spells
            for i in range(0, 9, 3):
                cols = st.columns(3) 
                row_cards = market_cards[i:i+3]
                for j in range(len(row_cards)):
                    with cols[j]:
                        card = row_cards[j]
                        st.image(card['ImageURL'], width=200)
                        st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})")
        
        except Exception as e:
            st.error("การสุ่มล้มเหลว! อาจเป็นเพราะ Content จากภาคเสริมที่เลือกไว้มีไม่เพียงพอ")
            st.error(f"รายละเอียด: {e}")

else:
    # --- หน้าจอเริ่มต้น ---
    st.info("⬅️ กรุณาตั้งค่าการเล่นในเมนูด้านซ้าย แล้วกดปุ่ม 'เริ่มสุ่ม!' เพื่อเริ่มต้น")