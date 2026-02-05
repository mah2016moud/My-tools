import streamlit as st
import requests

# 1. إعدادات التصميم النيون
st.set_page_config(page_title="Scout-X | Web Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 50%; width: 150px; height: 150px; text-align: center; margin: auto; }
    .card-rank { background: #161b22; border: 2px solid #00d4ff; border-radius: 12px; padding: 25px; height: 220px; }
    .card-mastery { background: #161b22; border: 2px solid #f2cc60; border-radius: 12px; padding: 25px; height: 220px; overflow: hidden; }
    .mastery-title { color: #f2cc60; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .mastery-list { list-style-type: disc; padding-left: 20px; font-size: 18px; line-height: 1.6; color: #c9d1d9; }
    .report-box { background: #0d1117; border: 1px solid #58a6ff; padding: 15px; border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {str(v['key']): v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs_map()

st.title("🎯 Scout-X | Master Web Edition")

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

    with st.spinner('Synchronizing...'):
        try:
            # 1. جلب بيانات الحساب الأساسية
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_data.get('id')
            
            # 2. جلب الرانك والماتشات والمستري (كل واحدة في try منفصلة لضمان العرض)
            try:
                ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            except: ranks = []

            try:
                mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            except: mastery = []

            try:
                m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
            except: m_ids = []

            # عرض الإحصائيات العلوية
            wins, roles = 0, []
            match_list = []
            for mid in m_ids:
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                for p in m_info['info']['participants']:
                    if p['puuid'] == puuid:
                        res = "WIN" if p['win'] else "LOSS"
                        if p['win']: wins += 1
                        roles.append(p.get('individualPosition', 'UNKNOWN'))
                        match_list.append({"CHAMPION": p['championName'], "RESULT": res, "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}", "GOLD": p['goldEarned'], "VISION": p.get('visionScore', 0), "FARM": p['totalMinionsKilled']})

            st.write("---")
            g1, g2, g3 = st.columns(3)
            with g1: st.markdown(f'<div class="stMetric"><p>WIN RATE</p><h3>{(wins/len(m_ids))*100 if m_ids else 0:.0f}%</h3></div>', unsafe_allow_html=True)
            with g2: 
                top_role = max(set(roles), key=roles.count) if roles else "N/A"
                st.markdown(f'<div class="stMetric" style="border-color:#f2cc60"><p>TOP ROLE</p><h3>{top_role}</h3></div>', unsafe_allow_html=True)
            with g3: st.markdown(f'<div class="stMetric" style="border-color:#58a6ff"><p>MATCHES</p><h3>{len(m_ids)}</h3></div>', unsafe_allow_html=True)

            # 3. عرض المربعات السفلية (الحل الجذري)
            st.write("---")
            b1, b2 = st.columns(2)
            with b1:
                rank_txt = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "UNRANKED"
                st.markdown(f'<div class="card-rank"><h3 style="color:#00d4ff">🏆 RANK DATA</h3><br><h2 style="color:white">{rank_txt}</h2></div>', unsafe_allow_html=True)
            
            with b2:
                # التأكد من مطابقة الـ ID لاسم البطل
                m_items = ""
                for c in mastery:
                    c_name = CHAMPS_MAP.get(str(c['championId']), "Champion")
                    m_items += f"<li>{c_name}: Lvl {c['championLevel']}</li>"
                
                if not m_items: m_items = "<li>No Mastery Data Found</li>"

                st.markdown(f"""
                    <div class="card-mastery">
                        <div class="mastery-title">⭐ TOP MASTERY</div>
                        <ul class="mastery-list">
                            {m_items}
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

            # الماتشات تحت
            st.subheader("Match History Reports")
            for m in match_list:
                with st.expander(f"🎮 {m['CHAMPION']} - {m['RESULT']} ({m['KDA']})"):
                    st.write(f"💰 Gold: {m['GOLD']:,} | 🎯 Farm: {m['FARM']}")

        except Exception as e:
            st.error(f"Critical Error: {e}")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
