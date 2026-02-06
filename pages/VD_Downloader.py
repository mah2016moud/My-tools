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
            'outtmpl': 'downloaded_video.%(ext)s', # اسم مؤقت للملف
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