import streamlit as st
import requests
import time
import math
from collections import Counter

# إعدادات الصفحة والتصميم النيون
st.set_page_config(page_title="Scout-X | Final Legendary Edition", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 150px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    
    /* حل مشكلة الدوائر المربعة نهائياً */
    .bubble-hero { 
        border: 4px solid #f2cc60; 
        border-radius: 50% !important; 
        object-fit: cover !important; 
        aspect-ratio: 1 / 1; 
        transition: 0.3s;
        display: block;
        margin: 0 auto;
    }
    .bubble-hero:hover { transform: scale(1.1); filter: brightness(1.2); box-shadow: 0 0 20px #f2cc60; }
    
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .animate-pulse { animation: pulse 3s infinite ease-in-out; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"
VERSION = "14.24.1" 

@st.cache_data(ttl=3600)
def get_champs_data():
    try:
        r = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/data/en_US/champion.json").json()
        name_to_id = {v['key']: v['id'] for v in r['data'].values()}
        id_to_name = {v['key']: v['name'] for v in r['data'].values()}
        return name_to_id, id_to_name
    except: return {}, {}

NAME_TO_ID, ID_TO_NAME = get_champs_data()

st.title("🎯 Scout-X | Final Legendary Edition")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Player#Tag")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("RUN DEEP ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        with st.status("Gathering Player Intel...", expanded=True) as status:
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            time.sleep(1.0)
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            
            r_data = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            ranks = r_data if isinstance(r_data, list) else []
            
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=15&api_key={API_KEY}").json()
            
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
            match_list = []
            lanes = []
            for mid in m_ids:
                time.sleep(0.5)
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_info:
                    for p in m_info['info']['participants']:
                        if p['puuid'] == puuid:
                            lanes.append(p.get('individualPosition', 'UNKNOWN'))
                            dur = max(1, m_info['info'].get('gameDuration', 0)/60)
                            match_list.append({
                                'win': p['win'], 'champ': p['championName'], 
                                'k': p['kills'], 'd': p['deaths'], 'a': p['assists'],
                                'gold': p['goldEarned'], 'cs_m': round(p['totalMinionsKilled']/dur, 1),
                                'vision': p.get('visionScore', 0)
                            })
            top_role = Counter(lanes).most_common(1)[0][0] if lanes else "UNKNOWN"
            status.update(label="Analysis Ready!", state="complete", expanded=False)

        # 1. الإحصائيات
        st.write("---")
        c1, c2, c3 = st.columns(3)
        wr = (sum(1 for m in match_list if m["win"])/len(match_list)*100) if match_list else 0
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{wr:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{top_role}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(match_list)}</h2></div>', unsafe_allow_html=True)

        # 2. الرانك والماستري
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            if ranks:
                for r in ranks: r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
            else: r_html += "• Unranked Player"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
        with b2:
            m_html = "<b>⭐ TOP 3 CHAMPIONS</b><hr>"
            for c in mastery[:3]:
                name = ID_TO_NAME.get(str(c['championId']), "Hero")
                m_html += f"• {name}: Lvl {c['championLevel']} ({c['championPoints']:,} pts)<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

        # 3. الماتش هيستوري (الصور والتقييمات)
        st.write("---")
        st.subheader("🎮 Match History & Performance Reports")
        for m in match_list:
            res_txt = "VICTORY" if m['win'] else "DEFEAT"
            res_clr = "#3fb950" if m['win'] else "#da3633"
            with st.expander(f"● {m['champ']} - {m['k']}/{m['d']}/{m['a']} ({res_txt})"):
                col_img, col_rep = st.columns([1, 4])
                with col_img: 
                    st.image(f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion/{m['champ']}.png", width=100)
                with col_rep:
                    # تقييم ذكي للأداء
                    rating = "Average"
                    if m['k'] > 10: rating = "⭐ Legendary Carry"
                    elif m['d'] > 10: rating = "🍔 Feeding Warning"
                    elif m['a'] > 15: rating = "🤝 Team Player"
                    
                    st.markdown(f"""
                        <div class="report-card">
                            <b style="color:{res_clr};">{res_txt} | Performance: {rating}</b><br>
                            💰 Gold: {m['gold']:,} | 🎯 Farm: {m['cs_m']} CS/m | 👁️ Vision: {m['vision']}
                        </div>
                    """, unsafe_allow_html=True)

        # 4. بابلز الماستري (الصور الدائرية الكاملة)
        st.write("---")
        st.subheader("🌌 Champion Mastery Cloud")
        if mastery:
            max_p = mastery[0].get('championPoints', 1)
            cloud = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:25px; background:#161b22; padding:30px; border-radius:20px;">'
            for c in mastery:
                c_img_id = NAME_TO_ID.get(str(c['championId']), "Unknown")
                pts = c['championPoints']
                sz = 75 + (math.sqrt(pts) / math.sqrt(max_p)) * 120
                cloud += f'''
                <div style="text-align:center; width:{sz+10}px;">
                    <img class="bubble-hero animate-pulse" 
                         src="https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion/{c_img_id}.png" 
                         style="width:{sz}px; height:{sz}px;">
                    <p style="font-size:12px; font-weight:bold; margin-top:10px; color:#f2cc60;">{pts:,}</p>
                </div>'''
            st.markdown(cloud + '</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("Riot ID not found. Check Name#Tag and Region.")

st.sidebar.caption("© 2026 | Developed by MAHMOUD ABDALLA")

