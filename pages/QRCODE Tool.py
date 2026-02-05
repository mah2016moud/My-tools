import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io
import os

# إعدادات الصفحة
st.set_page_config(page_title="QR Master Pro", layout="centered")

# دالة معالجة اللوجو الأسود
def process_logo(path, target_hex):
    img = Image.open(path).convert("RGBA")
    datas = img.getdata()
    new_data = []
    h = target_hex.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    for item in datas:
        if item[0] < 125 and item[1] < 125 and item[2] < 125:
            new_data.append((*rgb, 255))
        else:
            new_data.append((255, 255, 255, 0))
    img.putdata(new_data)
    return img

# الواجهة
st.title("🎨 QR Master Pro 2026")
url = st.text_input("Paste your link here:")

col1, col2 = st.columns(2)
with col1:
    color_name = st.selectbox("Pick Color:", ["Black", "Royal Blue", "Classic Red", "Forest Green", "Deep Purple"])
    colors = {"Black": "#000000", "Royal Blue": "#1a237e", "Classic Red": "#b71c1c", "Forest Green": "#1b5e20", "Deep Purple": "#800080"}
with col2:
    show_logo = st.checkbox("Include Logo", value=True)

if st.button("Generate QR Code"):
    if url:
        hex_color = colors[color_name]
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=hex_color, back_color="white").convert('RGBA')

        if show_logo:
            name_map = {"facebook": "fb_logo", "youtube": "yt_logo", "instagram": "ins_logo", "whatsapp": "wa_logo"}
            for key, val in name_map.items():
                if key in url.lower() and os.path.exists(val + ".png"):
                    icon = process_logo(val + ".png", hex_color)
                    qr_w, qr_h = img.size
                    icon_size = int(qr_w / 7)
                    icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                    draw = ImageDraw.Draw(img)
                    pad = 8
                    draw.ellipse([(qr_w//2-icon_size//2-pad), (qr_h//2-icon_size//2-pad), (qr_w//2+icon_size//2+pad), (qr_h//2+icon_size//2+pad)], fill="white")
                    img.paste(icon, ((qr_w-icon_size)//2, (qr_h-icon_size)//2), mask=icon)
                    break

        st.image(img, width=300)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Download PNG", buf.getvalue(), "qr_code.png", "image/png")

st.markdown("---")
st.caption("© 2026 | All Rights Reserved | MAHMOUD ABDALLA")
