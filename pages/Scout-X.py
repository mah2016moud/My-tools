import streamlit as st
import requests

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="Scout-X | Web Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 50%; width: 140px; height: 140px; text-align: center; margin: auto; }
    /* تنسيق المربعات السفلية مطابق تماماً لصورة الكمبيوتر */
    .mastery-container {
        background: #161b22; 
        border: 2px solid #f2cc60; 
        border-radius: 15px; 
        padding: 25px; 
        min-height: 250px;
        margin-top: 20px;
    }
    .rank-container {
        background: #161b22; 
        border: 2px solid #00d4ff; 
        border-radius: 15px; 
        padding: 25px; 
        min-height: 250px;
        margin-top: 20px;
    }
    .mastery-list-text {
        font-size: 20px;
        color: #c9d1d9;
        line-height: 2;
        list-style-type: disc;
        margin-left: 20px;
    }
    .section-title { color: #f2cc60; font-size: 26px; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs_map()

st.title("🎯 Scout-X | Master Web Edition")

# واجهة البحث
col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn:
    st.write(" ")
    analyze_btn = st.button("ANALYZE SYSTEM")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    try:
        # جلب الـ PUUID والماتشات
        acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
        puuid = acc['puuid']
        sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
        s_id = sum_data.get('id')
        
        # جلب الرانك والمستري
        ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
        mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
        m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

        # الدوائر العلوية (Win Rate / Top Role)
        wins, roles = 0, []
        for mid in m_ids:
            m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
            for p in m_info['info']['participants']:
                if p['puuid'] == puuid:
                    if p['win']: wins += 1
                    roles.append(p.get('individualPosition', 'UNKNOWN'))

        st.write("---")
        g1, g2, g3 = st.columns(3)
        with g1: st.markdown(f'<div class="stMetric"><p>WIN RATE</p><h3>{(wins/len(m_ids))*100:.0f}%</h3></div>', unsafe_allow_html=True)
        with g2: 
            top_role = max(set(roles), key=roles.count) if roles else "N/A"
            st.markdown(f'<div class="stMetric" style="border-color:#f2cc60"><p>TOP ROLE</p><h3>{top_role}</h3></div>', unsafe_allow_html=True)
        with g3: st.markdown(f'<div class="stMetric" style="border-color:#58a6ff"><p>MATCHES</p><h3>{len(m_ids)}</h3></div>', unsafe_allow_html=True)

        # المربعات السفلية - العرض الإجباري
        st.write("---")
        inf1, inf2 = st.columns(2)
        
        with inf1:
            rank_display = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "UNRANKED"
            st.markdown(f"""
                <div class="rank-container">
                    <div class="section-title" style="color:#00d4ff">🏆 RANK DATA</div>
                    <h1 style="color:white; font-size:40px">{rank_display}</h1>
                </div>
            """, unsafe_allow_html=True)
            
        with inf2:
            # هنا بنبني القائمة النصية زي نسخة الكمبيوتر بالظبط
            m_html = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Champion')}: Lvl {c['championLevel']}</li>" for c in mastery])
            st.markdown(f"""
                <div class="mastery-container">
                    <div class="section-title">⭐ TOP MASTERY</div>
                    <ul class="mastery-list-text">
                        {m_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    except Exception:
        st.error("Error connecting to Riot Servers. Please check your API Key.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
