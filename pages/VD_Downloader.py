import streamlit as st
import requests

st.title("🎬 محمل الفيديوهات (عن طريق وسيط)")

url_input = st.text_input("ضع رابط الفيديو (YouTube, TikTok, Instagram):")

if st.button("جلب رابط التحميل"):
    if url_input:
        with st.spinner("جاري التواصل مع الوسيط..."):
            # بنستخدم API وسيط (زي Cobalt كمثال)
            api_url = "https://api.cobalt.tools/api/json"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "url": url_input,
                "videoQuality": "720"
            }
            
            try:
                response = requests.post(api_url, json=data, headers=headers)
                result = response.json()
                
                if result.get("url"):
                    video_url = result["url"]
                    st.success("✅ تم إيجاد الفيديو!")
                    st.video(video_url) # معاينة
                    st.markdown(f'[⬇️ اضغط هنا لتحميل الفيديو مباشرة]({video_url})')
                else:
                    st.error("الوسيط لم يستطع جلب الفيديو، قد يكون الرابط غير مدعوم.")
            except Exception as e:
                st.error(f"فشل الاتصال بالوسيط: {e}")
