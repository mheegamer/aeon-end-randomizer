# ==============================================================================
# Aeon's End Randomizer - เวอร์ชันสำหรับ Deploy บน Streamlit Cloud
# ==============================================================================

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random

# (ส่วนของ Page Config และ CSS เหมือนเดิม)
st.set_page_config(page_title="Aeon's End Randomizer", page_icon="👹", layout="wide")
st.markdown("""...""") # (นำ CSS จากโค้ดเก่ามาใส่)

# --- ส่วนของการเชื่อมต่อกับ Google Sheets (ปรับปรุงใหม่) ---
@st.cache_data(ttl=600)
def load_data_from_sheet(sheet_name):
    try:
        # **ปรับแก้: อ่านข้อมูล credentials จาก st.secrets แทนไฟล์ .json**
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # YOUR_SHEET_NAME ควรตั้งไว้ใน st.secrets ด้วยเพื่อความปลอดภัย
        # แต่เพื่อความง่าย เราจะยังคงใส่ไว้ตรงๆ ก่อน
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

# (โค้ดส่วนที่เหลือทั้งหมดเหมือนกับเวอร์ชันล่าสุดของเราทุกประการ)
# ...
# ...
# ...
