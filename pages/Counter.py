import streamlit as st

# 1. إعدادات الصفحة (يجب أن تكون أول سطر)
st.set_page_config(page_title="حاسبة الخصومات | MAHMOUD ABDALLA", page_icon="💰")

# 2. نظام تسجيل الدخول (Username: 11, Password: 11)
def check_login():
    if "authenticated_calc" not in st.session_state:
        st.session_state["authenticated_calc"] = False

    if not st.session_state["authenticated_calc"]:
        st.title("🔒 تسجيل الدخول")
        
        # تصميم خانات الدخول
        with st.container():
            user_input = st.text_input("اسم المستخدم")
            pass_input = st.text_input("كلمة المرور", type="password")
            
            if st.button("دخول"):
                if user_input == "11" and pass_input == "11":
                    st.session_state["authenticated_calc"] = True
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        return False
    return True

# 3. تشغيل الحماية - إذا نجح الدخول يعرض باقي الكود
if check_login():
    # تنسيق مخصص (CSS)
    st.markdown("""
        <style>
        .stNumberInput div div input {
            text-align: center;
        }
        footer {
            visibility: hidden;
        }
        .footer-text {
            position: fixed;
            bottom: 20px;
            left: 0;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 14px;
            border-top: 1px solid #444;
            padding-top: 10px;
            background-color: #0e1117; /* لون خلفية ستريم ليت الافتراضي الداكن */
        }
        </style>
        """, unsafe_allow_html=True)

    # محتوى الحاسبة
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

            # عرض النتائج في بطاقات (Metrics)
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

    # تذييل الصفحة (Footer)
    st.markdown("""
        <div class="footer-text">
            © 2026 | All Rights Reserved | MAHMOUD ABDALLA
        </div>
        """, unsafe_allow_html=True)

    # زر تسجيل الخروج في القائمة الجانبية
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state["authenticated_calc"] = False
        st.rerun()
