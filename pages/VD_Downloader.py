import streamlit as st
import yt_dlp
import os
import time

# إعدادات واجهة الصفحة
st.set_page_config(page_title="Universal Video Downloader", page_icon="📥", layout="centered")

st.title("📥 Video Downloader Pro")
st.markdown("حمل فيديوهاتك المفضلة من YouTube, TikTok, Facebook, Instagram")

# حقل إدخال الرابط
url = st.text_input("انسخ رابط الفيديو هنا:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        # إعدادات متقدمة لتجنب الحظر (Error 403)
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
            }
        }

        with st.spinner('🚀 جاري استخراج البيانات وتحضير الفيديو...'):
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # الحصول على معلومات الفيديو أولاً
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                video_title = info.get('title', 'video')

            # التأكد من وجود الملف وعرضه
            if os.path.exists(file_path):
                st.success(f"✅ تم تجهيز: {video_title}")
                
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ اضغط هنا لبدء التحميل على جهازك",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
                
                # معاينة بسيطة للفيديو
                st.video(file_path)
                
    except Exception as e:
        st.error(f"❌ عذراً، حدث خطأ: {str(e)}")
        st.info("نصيحة: تأكد أن الرابط عام (Public) وليس خاصاً.")

st.divider()
st.caption("Powered by yt-dlp & Streamlit | 2026")
