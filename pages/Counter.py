import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة الخصومات |دعاء ربيع ", page_icon="💰")

# تنسيق مخصص لجعل الواجهة جذابة وتناسب الهوية المطلوبة
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a;
    }
    .stNumberInput div div input {
        text-align: center;
    }
    footer {
        visibility: hidden;
    }
    .footer-text {
        position: fixed;
        bottom: 20px;
        width: 100%;
        text-align: center;
        color: #888;
        font-size: 14px;
        border-top: 1px solid #444;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 حاسبة الخصومات والتحصيل")
st.write("أدخل البيانات بالأسفل لحساب النسبة المئوية والمبلغ المطلوب.")

# مدخلات المستخدم
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        original_price = st.number_input("المبلغ بالكامل (قبل الخصم)", min_value=0.0, step=1.0, format="%.2f")
    with col2:
        discounted_price = st.number_input("المبلغ بعد الخصم", min_value=0.0, step=1.0, format="%.2f")

# زر الحساب
if st.button("احسب النتائج"):
    if original_price > 0:
        # الحسابات
        discount_amount = original_price - discounted_price
        discount_percentage = (discount_amount / original_price) * 100
        sixty_percent_value = discounted_price * 0.60

        # عرض النتائج في بطاقات (Cards)
        st.divider()
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.metric(label="نسبة الخصم", value=f"{discount_percentage:.2f}%")
        
        with res_col2:
            st.metric(label="المبلغ المطلوب (60%)", value=f"{sixty_percent_value:,.2f} ج.م")
            
        if discounted_price > original_price:
            st.warning("تنبيه: السعر بعد الخصم أكبر من السعر الأصلي!")
    else:
        st.error("برجاء إدخال المبلغ الأصلي بشكل صحيح.")

# تذييل الصفحة (Footer) كما في الصورة
st.markdown("""
    <div class="footer-text">
        © 2026 | All Rights Reserved | MAHMOUD ABDALLA
    </div>
    """, unsafe_allow_html=True)