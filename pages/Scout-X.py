import streamlit as st
import requests
import time
import math
from collections import Counter

st.set_page_config(page_title="Scout-X | Funny Stable Edition", layout="wide")

# ستايل الـ Funny والـ Bouncing
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 180px; }
    
    /* أنيميشن مضحك للصور */
    @keyframes bounce { 
        0%, 100% { transform: translateY(0); } 
        50% { transform: translateY(-15px); } 
    }
    .funny-bounce { animation: bounce 2s infinite ease-in-out; cursor: pointer; transition: 0.3s; }
    .funny-bounce:hover { transform: scale(1.2) rotate(10deg); filter: brightness(1.2); }
    
    .report-card { background: #161b22; border-left: 5px solid #3fb950; padding: 10px; margin: 5px; border-radius: 5px; }
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

# القائمة الجانبية (ثبتناها عشان الماتشات ما تختفيش)
page = st.sidebar.selectbox("Go to", ["🏠 Home / Rank", "🎮 Match Reports", "☁️ Hero Cloud"])

st.title("🎯 Scout-X | Web Edition")

# إدخال البيانات
col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    if st.button("FETCH POWER"):
        name, tag = riot_id.split("#")
        m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
        plat, rout = m_[region]
        
        try:
            with st.status("Gathering Magic...", expanded=True) as status:
                acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
                st.session_state.puuid = acc['puuid']
                time.sleep(1.5)
                
                sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{st.session_state.puuid}?api_key={API_KEY}").json()
                s_id = sum_res.get('id')
                time.sleep(1.5)
                
                st.session_state.ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                time.sleep(1.5)
                
                st.session_state.mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{st.session_state.puuid}/top?count=15&api_key={API_KEY}").json()
                time.sleep(1.5)
                
                m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{st.session_state.puuid}/ids?count=10&api_key={API_KEY}").json()
                
                matches = []
                lanes = []
                for mid in m_ids:
                    time.sleep(0.8)
                    m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                    if 'info' in m_data:
                        for p in m_data['info']['participants']:
                            if p['puuid'] == st.session_state.puuid:
                                lanes.append(p.get('individualPosition', 'UNKNOWN'))
                                matches.append({
                                    'win': p['win'], 'champ': p['championName'], 'k': p['kills'], 'd': p['deaths'], 'a': p['assists'],
                                    'gold': p['goldEarned'], 'vision': p.get('visionScore', 0)
                                })
                st.session_state.matches = matches
                st.session_state.top_role = Counter(lanes).most_common(1)[0][0] if lanes else "AFK"
                status.update(label="Ready to Troll!", state="complete", expanded=False)
        except: st.error("Wrong ID or API Key! 🤡")

# العرض
if "puuid" in st.session_state:
    if page == "🏠 Home / Rank":
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="neon-box">WR: { (sum(1 for m in st.session_state.matches if m["win"])/len(st.session_state.matches)*100):.0f}% 🚀</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box">Main: {st.session_state.top_role} 🕹️</div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box">Matches: {len(st.session_state.matches)} ⚔️</div>', unsafe_allow_html=True)
        
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_txt = "<b>🏆 RANK</b><br>"
            if st.session_state.ranks:
                for r in st.session_state.ranks: r_txt += f"• {r.get('tier')} {r.get('rank')} 🔥<br>"
            else: r_txt += "• Unranked (Iron Soul? 💀)"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_txt}</div>', unsafe_allow_html=True)
        with b2:
            m_txt = "<b>⭐ BEST CHAMPS</b><br>"
            for c in st.session_state.mastery[:3]:
                name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                m_txt += f"• {name}: Lvl {c.get('championLevel')} 👑<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_txt}</div>', unsafe_allow_html=True)

    elif page == "🎮 Match Reports":
        st.subheader("Match History (The Good & The Ugly) 😂")
        for m in st.session_state.matches:
            emoji = "🔥" if m['win'] else "🤡"
            with st.expander(f"{emoji} {m['champ']} - {m['k']}/{m['d']}/{m['a']}"):
                st.write(f"💰 Gold: {m['gold']:,} | 👁️ Vision: {m['vision']}")
                if m['d'] > 10: st.warning("Stop Feeding! 🍔")
                elif m['k'] > 10: st.success("Carry Lord! 👑")

    elif page == "☁️ Hero Cloud":
        st.header("🌌 Hero Constellation")
        max_p = st.session_state.mastery[0].get('championPoints', 1)
        cloud = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:30px;">'
        for c in st.session_state.mastery:
            name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
            pts = c.get('championPoints', 0)
            sz = 60 + (math.sqrt(pts) / math.sqrt(max_p)) * 130
            cloud += f'''<div style="text-align:center;">
                         <img class="funny-bounce" src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{name}.png" 
                         style="width:{sz}px; height:{sz}px; border-radius:50%; border:3px solid #f2cc60;">
                         <p style="font-size:12px; font-weight:bold; margin-top:5px;">{pts:,} pts</p></div>'''
        st.markdown(cloud + '</div>', unsafe_allow_html=True)

st.sidebar.caption("© 2026 | Developed by MAHMOUD ABDALLA")
