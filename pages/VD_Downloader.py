import streamlit as st
import yt_dlp
import os

st.title("🎬 محمل فيديوهات بسيط")

url = st.text_input("الرابط:")

if st.button("تحميل"):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]', # بيجبره ياخد صيغة mp4 مباشرة
            'noplaylist': True,
            'quiet': True,
            # محاولة أخيرة للهيدرز البسيطة
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            
        with open(path, "rb") as f:
            st.download_button("💾 حفظ الفيديو", f, file_name=os.path.basename(path))
            
    except Exception as e:
        st.error("السيرفر السحابي محظور حالياً من يوتيوب.")
        st.info("💡 نصيحة: المواقع الكبيرة اللي بتحمل من يوتيوب بتدفع آلاف الدولارات عشان تغير الـ IP بتاعها كل ثانية. جرب تشغل الكود ده على جهازك (Local) وهيشتغل فوراً!")
