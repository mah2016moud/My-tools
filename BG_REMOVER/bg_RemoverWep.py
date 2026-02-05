import streamlit as st
from rembg import remove
from PIL import Image
import io
import sys
import os

# حل مشكلة الـ NoneType اللي ظهرت في الصورة الأولى
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

st.set_page_config(page_title="Mahmoud BG Remover", page_icon="✂️")

st.title("✂️ محترف إزالة الخلفية")
st.markdown("### برمجة: **MAHMOUD ABDALLA**")

# اختيار النوع
mode = st.selectbox("إختر نوع القص:", ("عام (تلقائي)", "أشخاص (دقة عالية)", "ملابس"))

uploaded_file = st.file_uploader("إختر صورة...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    input_image = Image.open(uploaded_file)
    st.image(input_image, caption="الصورة الأصلية", use_container_width=True)
    
    if st.button("إزالة الخلفية الآن ✨"):
        with st.spinner("جاري المعالجة..."):
            try:
                # المعالجة
                output_image = remove(input_image)
                
                # تحضير زر التحميل
                buf = io.BytesIO()
                output_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.image(output_image, caption="النتيجة", use_container_width=True)
                st.download_button(label="تحميل الصورة ⬇️", data=byte_im, file_name="output.png", mime="image/png")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.caption("© 2026 | MAHMOUD ABDALLA")