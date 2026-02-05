import streamlit as st
from rembg import remove
from PIL import Image
import io
import sys
import os

# Anti-crash for Streamlit Cloud
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

# Page Configuration
st.set_page_config(page_title="AI Background Remover", page_icon="✂️")

# Main Title
st.title("✂️ AI Background Remover")
st.write("Upload your image and remove the background instantly.")

# Sidebar Settings
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox(
        "Select Model Type:",
        ("General", "Human (High Precision)", "Clothing")
    )
    
    st.markdown("---")
    st.caption("Created by MAHMOUD ABDALLA")

# File Uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    input_image = Image.open(uploaded_file)
    
    # Show Original Image
    st.image(input_image, caption="Original Image", use_container_width=True)
    
    if st.button("Remove Background ✨"):
        with st.spinner("Processing... Please wait"):
            try:
                # Background Removal Process
                output_image = remove(input_image)
                
                # Prepare Download Button
                buf = io.BytesIO()
                output_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                # Show Result
                st.image(output_image, caption="Result", use_container_width=True)
                
                st.download_button(
                    label="Download Image ⬇️",
                    data=byte_im,
                    file_name=f"{uploaded_file.name}_no_bg.png",
                    mime="image/png"
                )
                st.success("Success!")
                
            except Exception as e:
                st.error(f"Error occurred: {e}")

# Footer (The small credit you asked for)
st.markdown("---")

st.caption("© 2026 | All Rights Reserved | MAHMOUD ABDALLA")
