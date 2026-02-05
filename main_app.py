import streamlit as st

# إعداد الصفحة العامة
st.set_page_config(page_title="Mahmoud's AI Hub", page_icon="🚀")

# القائمة الجانبية لاختيار المشروع
st.sidebar.title("🛠️ My Projects")
project = st.sidebar.radio("Go to:", ["Background Remover", "Project 2 (Soon)", "Project 3 (Soon)"])

# المنطق المسؤول عن تبديل المشاريع
if project == "Background Remover":
    # هنا هنحط كود قص الخلفية (النسخة الإنجليزية)
    st.title("✂️ AI Background Remover")
    # ... (باقي كود الـ Remover اللي عملناه) ...
    
elif project == "Project 2 (Soon)":
    st.title("🚀 Project 2")
    st.write("This project is under construction...")

# الحقوق في أسفل القائمة الجانبية
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 | MAHMOUD ABDALLA")
