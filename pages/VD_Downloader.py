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
            # تنظيف النسبة المئوية من أي أكواد ألوان أو رموز غريبة
            p_str = d.get('_percent_str', '0%').replace('%','')
            # إزالة أي مسافات أو رموز غير مرئية
            p_clean = "".join(filter(str.isdigit, p_str.split('.')[0]))
            val = float(p_clean) / 100
            progress_bar.progress(min(val, 1.0))
            status_placeholder.text(f"📥 جاري التحميل: {p_str}")
        except: pass

if st.button("بدء التحميل"):
    if url:
        try:
            if not os.path.exists("downloads"): os.makedirs("downloads")
            
            ydl_opts = {
                # حل مشكلة الـ Playlist (الصورة 4): منع تحميل القوائم تماماً
                'noplaylist': True, 
                # حل مشكلة الـ FFmpeg (الصورة 2): استخدام صيغة مدمجة لا تحتاج دمج
                'format': 'best[ext=mp4]/best', 
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'nocheckcertificate': True,
                # حل مشكلة 403 (الصورة 1 و 5): انتحال صفة متصفح أندرويد لتقليل الحظر
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
                'quiet': False,
                'no_warnings': False,
            }

            with st.spinner('جاري المعالجة... قد يستغرق الأمر دقيقة'):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # محاولة استخراج المعلومات والتحميل
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.success("✅ جاهز!")
                        st.download_button("⬇️ اضغط لحفظ الملف على جهازك", f, file_name=os.path.basename(file_path))
                
        except Exception as e:
            st.error(f"عذراً، حدث خطأ: {str(e)}")
            st.info("نصيحة: يوتيوب يميل لحظر السيرفرات السحابية. إذا استمر الخطأ 403، جرب الرابط بعد قليل أو استخدم فيديو آخر.")
    else:
        st.warning("الرجاء وضع رابط أولاً")
