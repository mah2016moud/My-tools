import streamlit as st
import requests
import time
import math
from collections import Counter

st.set_page_config(page_title="Scout-X | Ultimate Stable", layout="wide")

# التصميم النهائي المعتمد
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 150px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    
    @keyframes pulse-funny {
        0% { transform: scale(1); }
        50% { transform: scale(1.05) rotate(1deg); }
        100% { transform: scale(1); }
    }
    .bubble-hero { animation: pulse-funny 3s infinite ease-in-out; cursor: pointer; transition: 0.3s; border: 2px solid #f2cc60; border-radius: 50%; }
    .bubble-hero:hover { transform: scale(1.2) !important; z-index: 10; filter: brightness(1.2); }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"
VERSION = "14.24.1" # تحديث النسخة لضمان ظهور كل الصور

@st.cache_data(ttl=3600)
def get_champs_data():
    try:
        r = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/data/en_US/champion.json").json()
        # نستخدم الـ ID الفعلي للصورة بدل الاسم العادي
        name_to_id = {v['key']: v['id'] for v in r['data'].values()}
        id_to_name = {v['key']: v['name'] for v in r['data'].values()}
        return name_to_id, id_to_name
    except: return {}, {}

NAME_TO_ID, ID_TO_NAME = get_champs_data()

st.title("🎯 Scout-X | Ultimate Edition")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("RUN ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        with st.status("Fetching Data...", expanded=True) as status:
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            time.sleep(1.5)
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            time.sleep(1.5)
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=15&api_key={API_KEY}").json()
            time.sleep(1.5)
            
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
            match_list = []
            lanes = []
            for mid in m_ids:
                time.sleep(0.7)
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_info:
                    for p in m_info['info']['participants']:
                        if p['puuid'] == puuid:
                            lanes.append(p.get('individualPosition', 'UNKNOWN'))
                            dur = max(1, m_info['info'].get('gameDuration', 0)/60)
                            # هنا التعديل: نستخدم اسم الصورة الصحيح
                            match_list.append({
                                'win': p['win'], 'champ_id': p['championName'], 'name': p['championName'],
                                'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'gold': p['goldEarned'], 'cs_m': round(p['totalMinionsKilled']/dur, 1),
                                'vision': p.get('visionScore', 0)
                            })
            top_role = Counter(lanes).most_common(1)[0][0] if lanes else "UNKNOWN"
            status.update(label="Sync Complete!", state="complete", expanded=False)

        # الإحصائيات
        st.write("---")
        c1, c2, c3 = st.columns(3)
        wr = (sum(1 for m in match_list if m["win"])/len(match_list)*100) if match_list else 0
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{wr:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{top_role}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(match_list)}</h2></div>', unsafe_allow_html=True)

        # الرانك والماستري
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            if isinstance(ranks, list) and len(ranks) > 0:
                for r in ranks: r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
            else: r_html += "• Unranked"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
        with b2:
            m_html = "<b>⭐ TOP MASTERY</b><hr>"
            for c in mastery[:3]:
                c_name = ID_TO_NAME.get(str(c['championId']), "Hero")
                m_html += f"• {c_name}: Level {c['championLevel']}<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

        # الماتشات (حل مشكلة الصور هنا)
        st.write("---")
        st.subheader("🎮 Match History")
        for m in match_list:
            res_txt = "WIN" if m['win'] else "LOSS"
            res_clr = "#3fb950" if m['win'] else "#da3633"
            with st.expander(f"● {m['name']} - {m['kda']}"):
                col_img, col_rep = st.columns([1, 4])
                with col_img: 
                    # استخدام رابط الصورة المباشر من Riot
                    st.image(f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion/{m['champ_id']}.png", width=90)
                with col_rep:
                    st.markdown(f'<div class="report-card"><b style="color:{res_clr}">{res_txt}</b><br>💰 Gold: {m["gold"]:,} | 🎯 Farm: {m["cs_m"]} CS/m</div>', unsafe_allow_html=True)

        # بابلز الماستري (حل مشكلة الصور هنا أيضاً)
        st.write("---")
        st.subheader("🌌 Mastery Cloud")
        if mastery:
            max_p = mastery[0].get('championPoints', 1)
            cloud = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:20px; background:#161b22; padding:20px; border-radius:15px;">'
            for c in mastery:
                c_img_id = NAME_TO_ID.get(str(c['championId']), "Unknown")
                pts = c['championPoints']
                sz = 60 + (math.sqrt(pts) / math.sqrt(max_p)) * 110
                cloud += f'''<div style="text-align:center;">
                             <img class="bubble-hero" src="https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion/{c_img_id}.png" style="width:{sz}px; height:{sz}px;">
                             <p style="font-size:10px; margin-top:5px;">{pts:,}</p></div>'''
            st.markdown(cloud + '</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: Make sure the Name#Tag is correct.")

st.sidebar.caption("© 2026 | Developed by MAHMOUD ABDALLA")
