import streamlit as st
import os

# إعدادات الصفحة
st.set_page_config(page_title="Mahmoud's AI Hub", page_icon="🚀", layout="wide")

st.markdown("<h1 style='text-align: center;'>My Automated AI Portfolio 🚀</h1>", unsafe_allow_index=True)
st.markdown("<p style='text-align: center;'>All projects below are loaded automatically from the 'pages' directory.</p>", unsafe_allow_index=True)
st.markdown("---")

# وظيفة لجلب ملفات المشاريع من فولدر pages
def get_projects():
    project_files = []
    pages_dir = "pages"
    if os.path.exists(pages_dir):
        # بنجيب الملفات اللي بتنتهي بـ .py ومش بتبدأ بـ underscore
        files = [f for f in os.listdir(pages_dir) if f.endswith(".py") and not f.startswith("_")]
        files.sort() # عشان يظهروا بالترتيب اللي أنت مرقمه (01, 02..)
        for f in files:
            # تنظيف الاسم للعرض (نشيل الرقم والامتداد)
            display_name = f.replace(".py", "").replace("_", " ")
            if display_name[0:2].isdigit(): # لو بيبدأ برقم نشيله من الاسم المعروض
                display_name = display_name[3:]
            project_files.append({"file_path": f"pages/{f}", "name": display_name})
    return project_files

projects = get_projects()

if not projects:
    st.warning("No projects found in the 'pages' folder yet!")
else:
    # عرض المشاريع في شكل شبكة (Grid) من 3 أعمدة
    cols = st.columns(3)
    for index, project in enumerate(projects):
        with cols[index % 3]: # توزيع تلقائي على الـ 3 أعمدة
            st.markdown(f"### 🛠️ {project['name'].title()}")
            st.write("Click the button below to launch this tool.")
            if st.button(f"Launch Project →", key=project['file_path'], use_container_width=True):
                st.switch_page(project['file_path'])
            st.markdown("---")

# Footer
st.markdown("<p style='text-align: center; color: gray;'>© 2026 | MAHMOUD ABDALLA</p>", unsafe_allow_index=True)
