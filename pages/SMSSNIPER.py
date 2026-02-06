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

# إعدادات الواجهة
st.set_page_config(page_title="FAWATERAK GHOST", page_icon="⚡")

if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

def run_fawaterak_v10(phone):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # تمويه إضافي
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)
        
        driver.get("https://app.fawaterk.com/register")
        
        # ملء البيانات بناءً على ترتيب الصورة (Full Name, Business, Email, Password, Phone)
        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        
        if len(inputs) >= 5:
            inputs[0].send_keys("Mahmoud Dev") # Full Name
            inputs[1].send_keys("Ghost Solutions") # Business
            inputs[2].send_keys(f"user_{random.randint(1000,9999)}@gmail.com") # Email
            inputs[3].send_keys("StrongPass123!") # Password
            inputs[4].send_keys(phone) # Phone Number (المكان الصحيح بناءً على الصورة)
            
            # الموافقة على الشروط (Checkbox اللي في الصورة)
            check_box = driver.find_element(By.TYPE, "checkbox")
            driver.execute_script("arguments[0].click();", check_box)
            
            # ضغط زر Create Account
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create an Account')]")))
            driver.execute_script("arguments[0].click();", submit_btn)
            
            time.sleep(3)
            st.session_state.count += 1
            add_log("✅ Hit Confirmed!")
    except Exception:
        add_log("❌ Security Blocked (Bot Detected)")
    finally:
        if driver: driver.quit()

# --- UI ---
st.title("⚡ Fawaterak Sniper Elite")
target = st.text_input("Target Number", value="01124912480")

col1, col2 = st.columns(2)
if col1.button("🚀 START", use_container_width=True):
    st.session_state.running = True
if col2.button("🛑 STOP", use_container_width=True):
    st.session_state.running = False

st.metric("SUCCESS HITS", st.session_state.count)

# عرض اللوجز بدون إيرور الـ Label
st.text_area("Console Output", value="\n".join(st.session_state.logs[::-1]), height=200, disabled=True)

if st.session_state.running:
    run_fawaterak_v10(target)
    st.rerun()
