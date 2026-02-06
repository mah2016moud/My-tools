import streamlit as st
import yt_dlp
import os

# إعدادات الواجهة
st.set_page_config(page_title="Pro Video Downloader", page_icon="🚀")
st.title("🚀 المحمل الاحترافي السريع")

# حقل الإدخال
url = st.text_input("ضع الرابط هنا (فيديو واحد فقط):", placeholder="https://...")

# مكان حالة التحميل
status_placeholder = st.empty()
progress_bar = st.progress(0)

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            p = d.get('_percent_str', '0%').replace('%','')
            progress_bar.progress(float(p)/100)
            status_placeholder.text(f"📥 جاري التحميل: {p}%")
        except: pass

if st.button("بدء التحميل"):
    if url:
        try:
            if not os.path.exists("downloads"): os.makedirs("downloads")
            
            ydl_opts = {
                # الحل لمشكلة الـ Playlist (الصورة 4): منع تحميل القوائم
                'noplaylist': True, 
                # الحل لمشكلة الـ FFmpeg (الصورة 2): استخدام صيغة مدمجة لا تحتاج دمج
                'format': 'best[ext=mp4]/best', 
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'nocheckcertificate': True,
                # الحل لمشكلة 403 (الصورة 1 و 5): انتحال صفة متصفح أندرويد (أصعب في الحظر)
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            }

            with st.spinner('جاري المعالجة... قد يستغرق الأمر دقيقة'):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                
                with open(file_path, "rb") as f:
                    st.success("✅ جاهز!")
                    st.download_button("⬇️ اضغط لحفظ الملف على جهازك", f, file_name=os.path.basename(file_path))
                    
        except Exception as e:
            st.error(f"عذراً، يوتيوب حظر السيرفر حالياً (403) أو الرابط غير صالح. جرب رابط آخر.")
    else:
        st.warning("الرجاء وضع رابط أولاً")
