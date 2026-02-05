import streamlit as st
import os

# إعدادات الصفحة
st.set_page_config(page_title="Mahmoud's AI Hub", page_icon="🚀", layout="wide")

# العنوان الرئيسي مع تصحيح unsafe_allow_html
st.markdown("<h1 style='text-align: center;'>My Automated AI Portfolio 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Explore all projects automatically loaded from the 'pages' folder.</p>", unsafe_allow_html=True)
st.markdown("---")

# وظيفة لجلب المشاريع
def get_projects():
    project_files = []
    pages_dir = "pages"
    if os.path.exists(pages_dir):
        files = [f for f in os.listdir(pages_dir) if f.endswith(".py") and not f.startswith("_")]
        files.sort()
        for f in files:
            display_name = f.replace(".py", "").replace("_", " ")
            if display_name[0:2].isdigit():
                display_name = display_name[3:]
            project_files.append({"file_path": f"pages/{f}", "name": display_name})
    return project_files

projects = get_projects()

if not projects:
    st.info("Start by adding your first project inside the 'pages' folder!")
else:
    # عرض المشاريع في نص الشاشة
    cols = st.columns(3)
    for index, project in enumerate(projects):
        with cols[index % 3]:
            st.markdown(f"### 🛠️ {project['name'].title()}")
            st.write("Professional AI Tool")
            if st.button(f"Open {project['name']} →", key=project['file_path'], use_container_width=True):
                st.switch_page(project['file_path'])
            st.markdown("---")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>© 2026 | Developed by MAHMOUD ABDALLA</p>", unsafe_allow_html=True)
