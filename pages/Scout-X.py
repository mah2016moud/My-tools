import streamlit as st
import requests
import pandas as pd

# إعدادات الصفحة والتصميم النيون
st.set_page_config(page_title="Scout-X Web", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .win-text { color: #3fb950 !important; font-weight: bold; }
    .loss-text { color: #da3633 !important; font-weight: bold; }
    .card { background: #161b22; border-radius: 10px; padding: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# ملاحظة: الـ API Key ده مؤقت، لو وقف لازم تجدده من موقع Riot
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

st.title("🎯 Scout-X | Web Edition")

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col2:
    riot_id = st.text_input("Player ID (Name#Tag)", placeholder="Saeed#1111")
with col3:
    st.write(" ") 
    analyze_btn = st.button("ANALYZE SUBJECT")

if analyze_btn:
    if "#" not in riot_id:
        st.error("Format Error: Use Name#Tag")
    else:
        name, tag = riot_id.split("#")
        mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
        plat, rout = mapping[region]

        with st.spinner('Accessing Riot Servers...'):
            try:
                # خطوة 1: جلب PUUID
                acc_req = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}")
                if acc_req.status_code != 200:
                    st.error(f"Account Not Found or API Key Expired (Error {acc_req.status_code})")
                else:
                    acc_data = acc_req.json()
                    puuid = acc_data['puuid']
                    
                    # خطوة 2: جلب بيانات الـ Summoner (لتجنب خطأ الـ 'id')
                    sum_req = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}")
                    sum_data = sum_req.json()
                    s_id = sum_data.get('id')
                    
                    # خطوة 3: الرانك والماتشات
                    ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                    m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
                    
                    matches_list = []
                    wins = 0
                    for mid in m_ids:
                        m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                        for p in m_info['info']['participants']:
                            if p['puuid'] == puuid:
                                matches_list.append({
                                    "CHAMP": p['championName'],
                                    "RESULT": "WIN" if p['win'] else "LOSS",
                                    "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                    "GOLD": f"{p['goldEarned']:,}"
                                })
                                if p['win']: wins += 1

                    # العرض النهائي بالألوان المظبوطة
                    m1, m2, m3 = st.columns(3)
                    m1.metric("WIN RATE", f"{(wins/len(m_ids))*100:.0f}%")
                    m2.metric("RANK", ranks[0]['tier'] if ranks else "Unranked")
                    m3.metric("MATCHES", len(m_ids))

                    st.subheader("Recent Activity")
                    df = pd.DataFrame(matches_list)
                    
                    # تلوين الجدول (WIN بالأخضر و LOSS بالأحمر)
                    def style_result(v):
                        return 'color: #3fb950; font-weight: bold;' if v == 'WIN' else 'color: #da3633; font-weight: bold;'
                    
                    st.table(df.style.applymap(style_result, subset=['RESULT']))

            except Exception as e:
                st.error(f"System Error: {str(e)}")

st.divider()
st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
