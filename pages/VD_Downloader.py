import streamlit as st
import yt_dlp
import os

# إعدادات الواجهة
st.set_page_config(page_title="Ultra Video Downloader", page_icon="⚡", layout="centered")

st.title("⚡ المحمل الذكي (النسخة النهائية)")
st.markdown("حمل فيديوهاتك بدون حظر (يوتيوب، تيك توك، فيسبوك)")

# إدخال الرابط
url = st.text_input("ضع الرابط هنا:", placeholder="https://...")

# مكان حالة التحميل
status_ui = st.empty()
progress_bar = st.progress(0)

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            p_str = d.get('_percent_str', '0%').replace('%','')
            p_float = float(p_str) / 100
            progress_bar.progress(min(p_float, 1.0))
            status_ui.text(f"📥 جاري التحميل: {p_str}% | السرعة: {d.get('_speed_str', 'N/A')}")
        except: pass

if st.button("ابدأ التحميل الآن"):
    if url:
        try:
            # تنظيف المجلدات القديمة
            if not os.path.exists("downloads"): os.makedirs("downloads")
            
            ydl_opts = {
                'noplaylist': True, # منع تحميل قوائم التشغيل تماماً
                'format': 'best[ext=mp4]/best', # صيغة مدمجة لا تحتاج FFmpeg
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'nocheckcertificate': True,
                # استراتيجية تخطي الحظر (403 Forbidden)
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios'],
                        'skip': ['hls', 'dash']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                }
            }

            with st.spinner('🚀 جاري تخطي الحماية وتحضير الملف...'):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.success("✅ تم التحميل بنجاح!")
                        st.download_button(
                            label="💾 اضغط هنا لحفظ الملف على جهازك",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4"
                        )
        except Exception as e:
            st.error(f"خطأ: {str(e)}")
            st.info("إذا ظهر خطأ 403، يرجى المحاولة مرة أخرى بعد دقيقة أو استخدام رابط آخر.")
    else:
        st.warning("الرجاء إدخال رابط الفيديو أولاً!")

st.divider()
st.caption("ملاحظة: المتصفح سيقوم بحفظ الملف في مجلد التحميلات (Downloads) الافتراضي.")
