import streamlit as st
import yt_dlp
import os
import re

# إعدادات الصفحة
st.set_page_config(page_title="Video Downloader Pro", page_icon="🎬", layout="wide")

# CSS لتحسين شكل الواجهة
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 محمل الفيديوهات الذكي")
st.subheader("حمل من يوتيوب، تيك توك، وفيسبوك بضغطة زر")

# دالة لتحديث حالة التحميل (النسبة المئوية)
def progress_hook(d):
    if d['status'] == 'downloading':
        # تنظيف النص لاستخراج النسبة المئوية
        p = d.get('_percent_str', '0%')
        p = re.sub(r'\x1b\[[0-9;]*m', '', p) # إزالة أكواد الألوان
        percent = float(p.replace('%', '').strip())
        
        progress_bar.progress(percent / 100)
        status_text.text(f"📥 جاري التحميل: {p} | السرعة: {d.get('_speed_str', 'N/A')}")
    
    if d['status'] == 'finished':
        status_text.text("✅ اكتمل التحميل! جاري معالجة الملف...")

# المدخلات
url = st.text_input("ضع رابط الفيديو هنا:", placeholder="https://...")
quality = st.selectbox("اختر الجودة:", ["Best Quality", "720p", "480p", "Audio Only (MP3)"])

# مكان عرض شريط التقدم والحالة
status_text = st.empty()
progress_bar = st.progress(0)

if st.button("بدء عملية التحميل"):
    if not url:
        st.warning("رجاءً أدخل الرابط أولاً!")
    else:
        try:
            # إعدادات التحميل بناءً على الاختيار
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if quality != "Audio Only (MP3)" else 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                }
            }
            
            if quality == "Audio Only (MP3)":
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                # تصحيح الامتداد في حالة الـ MP3
                if quality == "Audio Only (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            # عرض زر التحميل النهائي للجهاز
            with open(file_path, "rb") as f:
                st.download_button(
                    label="💾 احفظ الملف الآن على جهازك",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="video/mp4" if quality != "Audio Only (MP3)" else "audio/mpeg"
                )
            st.balloons() # احتفال بسيط بالنجاح
            
        except Exception as e:
            st.error(f"خطأ: {str(e)}")

st.info("💡 ملاحظة: ملفات الويب تُحمل تلقائياً في فولدر (Downloads) الخاص بمتصفحك.")
