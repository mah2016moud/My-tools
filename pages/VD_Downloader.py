import streamlit as st
import yt_dlp
import os

# إعدادات الصفحة
st.set_page_config(page_title="Video Downloader", page_icon="📥")

st.title("📥 Video Downloader")
st.markdown("حمل فيديوهات من YouTube, TikTok, Facebook بكل سهولة")

# إدخال الرابط
url = st.text_input("ضع رابط الفيديو هنا:", placeholder="https://...")

if url:
    try:
        # إعدادات yt-dlp
       ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            # الإعدادات السحرية لتجنب الـ Block
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
            }
        }

        with st.spinner('جاري معالجة الفيديو...'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                video_title = info.get('title', 'video')

            # عرض زر التحميل للمستخدم
            with open(file_path, "rb") as file:
                st.video(file_path) # عرض معاينة للفيديو
                btn = st.download_button(
                    label="اضغط هنا لتحميل الفيديو على جهازك",
                    data=file,
                    file_name=f"{video_title}.mp4",
                    mime="video/mp4"
                )
            
            # مسح الملف من السيرفر بعد التحميل لتوفير المساحة
            if btn:
                os.remove(file_path)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")


st.info("ملاحظة: تأكد من تحديث مكتبة yt-dlp باستمرار.")
