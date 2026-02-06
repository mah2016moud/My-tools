import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Ultra Downloader", page_icon="⚡")
st.title("⚡ محمل الفيديوهات السريع")

url = st.text_input("ضع الرابط هنا:")

if st.button("تحميل"):
    if url:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').replace('%','')
                    progress_bar.progress(float(p)/100)
                    status_text.text(f"📥 جاري التحميل: {p}%")
                except: pass

        try:
            # إعدادات قوية جداً لتخطي حظر 403 ومنع الـ Playlist
           ydl_opts = {
    'format': 'best',
    'noplaylist': True,
    'nocheckcertificate': True,
    # التعديل السحري هنا: استخدام كليبات يوتيوب المخصصة للأجهزة المخففة
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'],
            'skip': ['hls', 'dash']
        }
    },
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/19.01.33 (Linux; U; Android 11) Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
    }
            }

            with st.spinner('🚀 جاري محايلة يوتيوب...'):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ydl.prepare_filename(info)

                with open(path, "rb") as f:
                    st.success("✅ هانت! الفيديو جاهز")
                    st.download_button("💾 سيف الفيديو على جهازك", f, file_name=os.path.basename(path))
                    
        except Exception as e:
            st.error(f"يوتيوب لسه قافل السيرفر (Error 403).")
            st.info("💡 جرب تحمل فيديو 'قصير' (Shorts) أو جرب مرة تانية كمان 5 دقائق.")
    else:
        st.warning("حط الرابط الأول!")

