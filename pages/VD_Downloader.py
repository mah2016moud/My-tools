import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Video Downloader Pro", page_icon="🎬")

st.title("🎬 محمل الفيديوهات الذكي")

url = st.text_input("ضع رابط الفيديو هنا:", placeholder="https://...")

# دالة تحديث البروجرس بار
def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%').replace('%','')
        try:
            progress_bar.progress(float(p)/100)
            status_text.text(f"📥 جاري التحميل... {p}%")
        except: pass

if st.button("بدء عملية التحميل"):
    if url:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            ydl_opts = {
                # 'best' بتجيب فيديو وصوت مدمجين جاهز لو مفيش ffmpeg
                'format': 'best', 
                'progress_hooks': [progress_hook],
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, "rb") as f:
                st.success("✅ تم التحميل بنجاح!")
                st.download_button(
                    label="💾 احفظ الفيديو الآن",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="video/mp4"
                )
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")
    else:
        st.warning("دخل اللينك الأول يا صاحبي!")
