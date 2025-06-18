# ==============================================================================
# Aeon's End Randomizer - Final Version (Optimize Random & Multi-Language)
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

# --- 4. ระบบสองภาษา (Internationalization) ---
LANGUAGES = {
    "ไทย": {
        "app_title": "🔮 Aeon's End Randomizer",
        "sidebar_header": "⚙️ ตั้งค่าการสุ่ม",
        "lang_select": "ภาษา / Language",
        "exp_select_header": "เลือกภาคเสริมที่จะใช้",
        "exp_select_label": "ภาคเสริม:",
        "no_card_data_warning": "ไม่พบข้อมูลการ์ด",
        "style_select_header": "สไตล์การสุ่ม",
        "style_true_random": "สุ่มสมบูรณ์ (True Random)",
        "style_optimize": "ปรับให้เล่นง่ายขึ้น (Optimize)",
        "mode_select_header": "เลือกโหมดการเล่น",
        "mode_expedition": "เล่นยาว (Expedition)",
        "mode_single_game": "เกมเดียว (Single Game)",
        "random_button": "🎲 เริ่มสุ่ม!",
        "initial_screen_info": "⬅️ กรุณาตั้งค่าการเล่นในเมนูด้านซ้าย แล้วกดปุ่ม 'เริ่มสุ่ม!' เพื่อเริ่มต้น",
        "random_fail_header": "การสุ่มล้มเหลว!",
        "random_fail_reason": "อาจเป็นเพราะ Content จากภาคเสริมที่เลือกไว้มีไม่เพียงพอ",
        "expedition_results_header": "ผลการสุ่มสำหรับ: 🗺️ เล่นยาว (Expedition)",
        "single_game_results_header": "ผลการสุ่มสำหรับ: ⚔️ เกมเดียว (Single Game)",
        "initial_market_header": "🛒 ตลาดเริ่มต้น (Initial Market)",
        "mage_pool_header": "👥 กลุ่ม Mage สำหรับเริ่มต้น (เลือก 4 คน)",
        "battle_1_header": "👹 Battle 1: เผชิญหน้ากับ",
        "battle_2_header": "👹 Battle 2: เผชิญหน้ากับ",
        "battle_3_header": "👹 Battle 3: เผชิญหน้ากับ",
        "battle_4_header": "👹 Battle 4 (Final Boss): เผชิญหน้ากับ",
        "treasure_reward_header": "💎 รางวัลจากด่านที่",
        "treasure_reward_subheader": "(เลือกรับจาก 3 ใบนี้)",
        "replacement_market_header": "🔄 การ์ดตลาดใหม่ 3 ใบ (สำหรับเติม)",
        "nemesis_encounter_header": "คุณจะต้องเผชิญหน้ากับ:",
        "mage_selection_header": "เหล่าผู้วิเศษผู้ถูกเลือก (4 คน):",
        "market_header": "การ์ดในตลาด (Market):",
    },
    "ENG": {
        "app_title": "🔮 Aeon's End Randomizer",
        "sidebar_header": "⚙️ Randomizer Settings",
        "lang_select": "Language / ภาษา",
        "exp_select_header": "Select Expansions to Use",
        "exp_select_label": "Expansions:",
        "no_card_data_warning": "Card data not found",
        "style_select_header": "Randomization Style",
        "style_true_random": "True Random",
        "style_optimize": "Optimized for Easier Start",
        "mode_select_header": "Select Game Mode",
        "mode_expedition": "Expedition",
        "mode_single_game": "Single Game",
        "random_button": "🎲 Randomize!",
        "initial_screen_info": "⬅️ Please configure settings in the sidebar and press 'Randomize!' to begin",
        "random_fail_header": "Randomization Failed!",
        "random_fail_reason": "There might not be enough content from the selected expansions.",
        "expedition_results_header": "Results for: 🗺️ Expedition",
        "single_game_results_header": "Results for: ⚔️ Single Game",
        "initial_market_header": "🛒 Initial Market",
        "mage_pool_header": "👥 Starting Mage Pool (Choose 4)",
        "battle_1_header": "👹 Battle 1: Face",
        "battle_2_header": "👹 Battle 2: Face",
        "battle_3_header": "👹 Battle 3: Face",
        "battle_4_header": "👹 Battle 4 (Final Boss): Face",
        "treasure_reward_header": "💎 Treasure Reward from Tier",
        "treasure_reward_subheader": "(Choose from these 3 cards)",
        "replacement_market_header": "🔄 3 New Market Cards (for replacement)",
        "nemesis_encounter_header": "You will face:",
        "mage_selection_header": "The chosen Mages (4):",
        "market_header": "Market Cards:",
    }
}

# --- 5. ส่วนของการเชื่อมต่อกับ Google Sheets ---
@st.cache_data(ttl=600)
def load_data_from_sheet(sheet_name):
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception:
        try:
            scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        except Exception as e_local:
            st.sidebar.error("Credential Error. Check secrets or credentials.json.")
            return pd.DataFrame()
            
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open("Aeon's End - Game Data")
        worksheet = spreadsheet.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        if 'Level' in df.columns:
            df['Level'] = pd.to_numeric(df['Level'], errors='coerce').fillna(0).astype(int)
        if 'Cost' in df.columns:
            df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading sheet '{sheet_name}'.")
        return pd.DataFrame()

# --- 6. โหลดข้อมูลทั้งหมด ---
with st.spinner('Loading card data from Google Sheets...'):
    df_mages_full = load_data_from_sheet("Mages")
    df_nemeses_full = load_data_from_sheet("Nemeses")
    df_cards_full = load_data_from_sheet("Cards")
    df_treasures_full = load_data_from_sheet("Treasures")

# --- 7. ส่วนควบคุมใน Sidebar ---
lang_code = st.sidebar.radio(LANGUAGES["ไทย"]["lang_select"], ["ไทย", "ENG"], horizontal=True)
t = LANGUAGES[lang_code]

st.title(t["app_title"])
st.sidebar.header(t["sidebar_header"])

st.sidebar.subheader(t["exp_select_header"])
if not df_cards_full.empty:
    expansions = pd.concat([df_mages_full['Expansion'], df_nemeses_full['Expansion'], df_cards_full['Expansion'], df_treasures_full['Expansion']]).dropna().unique().tolist()
    selected_expansions = []
    # Using a unique key for each checkbox that changes with the language to avoid state conflicts
    for expansion in sorted(expansions):
        if st.sidebar.checkbox(expansion, value=True, key=f"exp_{expansion}_{lang_code}"):
            selected_expansions.append(expansion)
else:
    selected_expansions = []
    st.sidebar.warning(t["no_card_data_warning"])

st.sidebar.divider()

st.sidebar.subheader(t["style_select_header"])
randomization_style = st.sidebar.radio(
    "Randomization Style", 
    [t["style_true_random"], t["style_optimize"]], 
    horizontal=True, 
    label_visibility="collapsed"
)

st.sidebar.divider()

game_mode = st.sidebar.selectbox(
    t["mode_select_header"],
    [t["mode_expedition"], t["mode_single_game"]]
)

if st.sidebar.button(t["random_button"]):
    df_mages = df_mages_full[df_mages_full['Expansion'].isin(selected_expansions)]
    df_nemeses = df_nemeses_full[df_nemeses_full['Expansion'].isin(selected_expansions)]
    df_cards = df_cards_full[df_cards_full['Expansion'].isin(selected_expansions)]
    df_treasures = df_treasures_full[df_treasures_full['Expansion'].isin(selected_expansions)]
    
    if game_mode == t["mode_expedition"]:
        st.header(t["expedition_results_header"])
        try:
            mages = df_mages.sample(4)
            nemesis_1 = df_nemeses[df_nemeses['Level'] == 1].sample(1).iloc[0]
            nemesis_2 = df_nemeses[df_nemeses['Level'] == 2].sample(1).iloc[0]
            nemesis_3 = df_nemeses[df_nemeses['Level'] == 3].sample(1).iloc[0]
            nemesis_4 = df_nemeses[df_nemeses['Level'] == 4].sample(1).iloc[0]

            # --- New Market Logic for Expedition ---
            gems_pool = df_cards[df_cards['Type'] == 'Gem']
            if randomization_style == t["style_optimize"]:
                cheap_gems = gems_pool[gems_pool['Cost'].isin([2, 3])]
                if not cheap_gems.empty:
                    first_gem = cheap_gems.sample(1)
                    remaining_gems_pool = gems_pool.drop(first_gem.index)
                    other_gems = remaining_gems_pool.sample(2)
                    initial_gems = pd.concat([first_gem, other_gems])
                else:
                    initial_gems = gems_pool.sample(3)
            else: # True Random
                initial_gems = gems_pool.sample(3)

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
            
            tab_list = [f"▶️ Setup & Battle 1", f"⚔️ Battle 2", f"⚔️ Battle 3", f"👹 Battle 4 (Final)"]
            tab1, tab2, tab3, tab4 = st.tabs(tab_list)

            with tab1:
                st.subheader(t["initial_market_header"])
                market_cards = initial_market_df.to_dict('records')
                for i in range(0, 9, 3):
                    cols = st.columns(3) 
                    row_cards = market_cards[i:i+3]
                    for j in range(len(row_cards)):
                        with cols[j]:
                            card = row_cards[j]
                            st.image(card['ImageURL'], width=200)
                            st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})<br>*{card.get('Expansion', '')}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["mage_pool_header"])
                cols = st.columns(4)
                for i, mage in enumerate(mages.itertuples()):
                    with cols[i]:
                        st.image(mage.ImageURL, width=200)
                        st.caption(f"**{mage.Name}**<br>*{mage.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["battle_1_header"])
                st.title(nemesis_1['Name'])
                st.image(nemesis_1['ImageURL'], width=250)
                st.caption(f"*{nemesis_1['Expansion']}*")
            
            with tab2:
                st.subheader(f'{t["treasure_reward_header"]} 1 {t["treasure_reward_subheader"]}')
                cols = st.columns(3)
                for i, tr in enumerate(treasures_1.itertuples()):
                    with cols[i]:
                        st.image(tr.ImageURL, width=200)
                        st.caption(f"**{tr.Name}** (Level {tr.Level})<br>*{tr.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["replacement_market_header"])
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_1.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})<br>*{card.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["battle_2_header"])
                st.title(nemesis_2['Name'])
                st.image(nemesis_2['ImageURL'], width=250)
                st.caption(f"*{nemesis_2['Expansion']}*")

            with tab3:
                st.subheader(f'{t["treasure_reward_header"]} 2 {t["treasure_reward_subheader"]}')
                cols = st.columns(3)
                for i, tr in enumerate(treasures_2.itertuples()):
                    with cols[i]:
                        st.image(tr.ImageURL, width=200)
                        st.caption(f"**{tr.Name}** (Level {tr.Level})<br>*{tr.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["replacement_market_header"])
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_2.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})<br>*{card.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["battle_3_header"])
                st.title(nemesis_3['Name'])
                st.image(nemesis_3['ImageURL'], width=250)
                st.caption(f"*{nemesis_3['Expansion']}*")

            with tab4:
                st.subheader(f'{t["treasure_reward_header"]} 3 {t["treasure_reward_subheader"]}')
                cols = st.columns(3)
                for i, tr in enumerate(treasures_3.itertuples()):
                    with cols[i]:
                        st.image(tr.ImageURL, width=200)
                        st.caption(f"**{tr.Name}** (Level {tr.Level})<br>*{tr.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["replacement_market_header"])
                cols = st.columns(3)
                for i, card in enumerate(replacement_market_3.itertuples()):
                     with cols[i]:
                        st.image(card.ImageURL, width=200)
                        st.caption(f"**{card.Name}** (Cost: {card.Cost})<br>*{card.Expansion}*", unsafe_allow_html=True)
                st.divider()
                st.subheader(t["battle_4_header"])
                st.title(nemesis_4['Name'])
                st.image(nemesis_4['ImageURL'], width=250)
                st.caption(f"*{nemesis_4['Expansion']}*")

        except Exception as e:
            st.error(t["random_fail_header"])
            st.error(f'{t["random_fail_reason"]}: {e}')

    else: # Single Game
        st.header(t["single_game_results_header"])
        try:
            nemesis = df_nemeses.sample(1).iloc[0]
            mages = df_mages.sample(4)
            
            gems_pool = df_cards[df_cards['Type'] == 'Gem']
            if randomization_style == t["style_optimize"]:
                cheap_gems = gems_pool[gems_pool['Cost'].isin([2, 3])]
                if not cheap_gems.empty:
                    first_gem = cheap_gems.sample(1)
                    remaining_gems_pool = gems_pool.drop(first_gem.index)
                    other_gems = remaining_gems_pool.sample(2)
                    gems = pd.concat([first_gem, other_gems])
                else: 
                    gems = gems_pool.sample(3)
            else: # True Random
                gems = gems_pool.sample(3)

            relics = df_cards[df_cards['Type'] == 'Relic'].sample(2)
            spells = df_cards[df_cards['Type'] == 'Spell'].sample(4)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(nemesis['ImageURL'], width=250)
                st.caption(f"**{nemesis['Name']}**<br>*{nemesis['Expansion']}*", unsafe_allow_html=True)
            with col2:
                st.subheader(t["nemesis_encounter_header"])
                st.title(f"👹 {nemesis['Name']}")
            st.divider()

            st.subheader(t["mage_selection_header"])
            cols = st.columns(4)
            for i, mage in enumerate(mages.itertuples()):
                with cols[i]:
                    st.image(mage.ImageURL, width=200) 
                    st.caption(f"**{mage.Name}**<br>*{mage.Expansion}*", unsafe_allow_html=True)
            st.divider()

            st.subheader(t["market_header"])
            market_cards = pd.concat([gems, relics, spells]).to_dict('records')
            for i in range(0, 9, 3):
                cols = st.columns(3) 
                row_cards = market_cards[i:i+3]
                for j in range(len(row_cards)):
                    with cols[j]:
                        card = row_cards[j]
                        st.image(card['ImageURL'], width=200)
                        st.caption(f"**{card.get('Name', '')}** (Cost: {card.get('Cost', 'N/A')})<br>*{card.get('Expansion', '')}*", unsafe_allow_html=True)
        
        except Exception as e:
            st.error(t["random_fail_header"])
            st.error(f'{t["random_fail_reason"]}: {e}')
else:
    st.info(t["initial_screen_info"])
