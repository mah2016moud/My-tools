import streamlit as st
import requests
import pandas as pd

# 1. إعدادات التصميم والدوائر
st.set_page_config(page_title="Scout-X | Web Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 50%; width: 150px; height: 150px; text-align: center; margin: auto; }
    .win-text { color: #3fb950 !important; font-weight: bold; }
    .loss-text { color: #da3633 !important; font-weight: bold; }
    .card-rank { background: #161b22; border: 2px solid #00d4ff; border-radius: 12px; padding: 20px; height: 100%; }
    /* ستايل جديد لعرض الأبطال بشكل شيك */
    .mastery-item { background: #0d1117; border: 1px solid #f2cc60; border-radius: 10px; padding: 10px; text-align: center; }
    .report-box { background: #0d1117; border: 1px solid #58a6ff; padding: 15px; border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# الـ API KEY - (لو ظهر إيرور تأكد من تجديده)
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
with col_srv:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id:
    riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn:
    st.write(" ")
    analyze_btn = st.button("ANALYZE SYSTEM")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    with st.spinner('Synchronizing with Riot Data...'):
        try:
            # 1. طلب البيانات الأساسية
            acc_req = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}")
            acc = acc_req.json()
            puuid = acc['puuid']
            
            sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_data.get('id')
            
            # جلب الرانك والمستري والماتشات
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

            # 2. عرض الدوائر الثلاثية
            match_list = []
            wins, roles = 0, []
            for mid in m_ids:
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                for p in m_info['info']['participants']:
                    if p['puuid'] == puuid:
                        res = "WIN" if p['win'] else "LOSS"
                        if p['win']: wins += 1
                        roles.append(p.get('individualPosition', 'UNKNOWN'))
                        match_list.append({
                            "CHAMPION": p['championName'],
                            "RESULT": res,
                            "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                            "GOLD": p['goldEarned'],
                            "VISION": p.get('visionScore', 0),
                            "FARM": p['totalMinionsKilled']
                        })

            st.write("---")
            g1, g2, g3 = st.columns(3)
            with g1: st.markdown(f'<div class="stMetric"><p>WIN RATE</p><h3>{(wins/len(m_ids))*100:.0f}%</h3></div>', unsafe_allow_html=True)
            with g2: 
                top_role = max(set(roles), key=roles.count) if roles else "N/A"
                st.markdown(f'<div class="stMetric" style="border-color:#f2cc60"><p>TOP ROLE</p><h3>{top_role}</h3></div>', unsafe_allow_html=True)
            with g3: st.markdown(f'<div class="stMetric" style="border-color:#58a6ff"><p>MATCHES</p><h3>{len(m_ids)}</h3></div>', unsafe_allow_html=True)

            # 3. تاريخ الماتشات والتقارير
            st.subheader("Match History & Performance Reports")
            for i, m in enumerate(match_list):
                with st.expander(f"🎮 {m['CHAMPION']} - {m['RESULT']} ({m['KDA']})"):
                    col_img, col_rep = st.columns([1, 3])
                    with col_img:
                        st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['CHAMPION']}.png", width=100)
                    with col_rep:
                        st.markdown(f"""
                        <div class="report-box">
                            <b style="color:{'#3fb950' if m['RESULT']=='WIN' else '#da3633'}">{m['RESULT']} REPORT</b><br>
                            💰 Gold: {m['GOLD']:,} | 🎯 Farm: {m['FARM']} | 👁️ Vision: {m['VISION']}
                        </div>
                        """, unsafe_allow_html=True)

            # 4. المربعات السفلية (الرانك والتوب 3 شامبيون بصورهم)
            st.write("---")
            b1, b2 = st.columns([1, 2])
            with b1:
                rank_txt = f"{ranks[0]['tier']} {ranks[0]['rank']} ({ranks[0]['leaguePoints']} LP)" if ranks else "UNRANKED"
                st.markdown(f'<div class="card-rank"><h3>🏆 PLAYER RANK</h3><br><b>{rank_txt}</b></div>', unsafe_allow_html=True)
            
            with b2:
                st.markdown('<div style="background:#161b22; border:2px solid #f2cc60; border-radius:12px; padding:20px;"><h3>⭐ TOP 3 MASTERY</h3>', unsafe_allow_html=True)
                m_cols = st.columns(3)
                for i, champ in enumerate(mastery):
                    c_name = CHAMPS_MAP.get(str(champ['championId']), 'Unknown')
                    with m_cols[i]:
                        st.markdown(f"""
                        <div class="mastery-item">
                            <img src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{c_name}.png" width="60" style="border-radius:50%"><br>
                            <b>{c_name}</b><br>Lvl {champ['championLevel']}
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            # تم تحسين معالجة الأخطاء هنا لمنع الـ Synchronization Error غير المبرر
            st.error(f"Error: {str(e)}. Please make sure the API Key is valid.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
