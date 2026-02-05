import streamlit as st
import requests
import time
import math
from collections import Counter

st.set_page_config(page_title="Scout-X | Final Edition v4.0", layout="wide")

# تصميم النيون والأنيميشن
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 180px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
    .champ-circle { transition: transform 0.3s; cursor: pointer; animation: float 3s ease-in-out infinite; }
    .champ-circle:hover { transform: scale(1.1) rotate(5deg); box-shadow: 0 0 25px rgba(242, 204, 96, 0.6); }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {str(v['key']): v['name'] for v in r['data'].values()}
    except: return {}

CHAMPS_MAP = get_champs_map()

page = st.sidebar.radio("Navigate", ["Player Scout", "Mastery Cloud"])
st.title("🎯 Scout-X | Final Edition v4.0")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("RUN DEEP ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        with st.status("Syncing Data...", expanded=True) as status:
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            st.session_state.puuid = acc['puuid']
            time.sleep(2.0)
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{st.session_state.puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            time.sleep(2.0)
            
            # حل الايرور: نتأكد إننا بنخزن داتا صح
            r_data = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            st.session_state.ranks = r_data if isinstance(r_data, list) else []
            
            time.sleep(2.0)
            m_data_top = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{st.session_state.puuid}/top?count=20&api_key={API_KEY}").json()
            st.session_state.mastery = m_data_top if isinstance(m_data_top, list) else []
            
            time.sleep(2.0)
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{st.session_state.puuid}/ids?count=10&api_key={API_KEY}").json()
            
            match_list = []
            lanes = []
            if isinstance(m_ids, list):
                for mid in m_ids:
                    time.sleep(1.0)
                    m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                    if 'info' in m_info:
                        for p in m_info['info']['participants']:
                            if p['puuid'] == st.session_state.puuid:
                                lanes.append(p.get('individualPosition', 'UNKNOWN'))
                                dur = max(1, m_info['info'].get('gameDuration', 0)/60)
                                match_list.append({
                                    'win': p['win'], 'champ': p['championName'], 'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                    'gold': p['goldEarned'], 'cs_m': round(p['totalMinionsKilled']/dur, 1),
                                    'vision': p.get('visionScore', 0)
                                })
            st.session_state.match_list = match_list
            st.session_state.top_role = Counter(lanes).most_common(1)[0][0] if lanes else "UNKNOWN"
            status.update(label="Complete!", state="complete", expanded=False)
    except: st.error("Sync Error. Check API Key or Name.")

if "puuid" in st.session_state:
    if page == "Player Scout":
        c1, c2, c3 = st.columns(3)
        wr = (sum(1 for m in st.session_state.match_list if m["win"])/len(st.session_state.match_list)*100) if st.session_state.match_list else 0
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{wr:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{st.session_state.top_role}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(st.session_state.match_list)}</h2></div>', unsafe_allow_html=True)

        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            # حماية السطر 111
            if st.session_state.ranks:
                for r in st.session_state.ranks:
                    r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
            else: r_html += "• Unranked or Data Private"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
        with b2:
            m_html = "<b>⭐ TOP MASTERY</b><hr>"
            for c in st.session_state.mastery[:3]:
                name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                m_html += f"• {name}: Level {c.get('championLevel')}<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

    elif page == "Mastery Cloud":
        st.header("🌌 Champion Mastery Constellation")
        if st.session_state.mastery:
            max_p = st.session_state.mastery[0].get('championPoints', 1)
            cloud = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:25px; background:#0d1117; padding:30px; border-radius:20px;">'
            for c in st.session_state.mastery:
                name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                sz = 60 + (math.sqrt(c.get('championPoints', 0)) / math.sqrt(max_p)) * 140
                cloud += f'''<div style="text-align:center;"><img class="champ-circle" src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{name}.png" 
                             style="width:{sz}px; height:{sz}px; border-radius:50%; border:3px solid #f2cc60;" title="{name}">
                             <p style="font-size:10px; margin-top:5px;">{name}</p></div>'''
            st.markdown(cloud + '</div>', unsafe_allow_html=True)

st.sidebar.caption("© 2026 | Developed by MAHMOUD ABDALLA")
