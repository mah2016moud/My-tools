import streamlit as st
import requests
import time
import math
from collections import Counter

st.set_page_config(page_title="Scout-X | Unified Professional Dashboard", layout="wide")

# تصميم احترافي جاد مع أنيميشن البابلز
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 150px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    
    /* أنيميشن البابلز المضحك (نبض عشوائي) */
    @keyframes pulse-funny {
        0% { transform: scale(1); }
        50% { transform: scale(1.05) rotate(2deg); }
        100% { transform: scale(1); }
    }
    .bubble-hero { animation: pulse-funny 3s infinite ease-in-out; cursor: pointer; transition: 0.3s; }
    .bubble-hero:hover { transform: scale(1.2) !important; z-index: 10; filter: brightness(1.3); }
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

st.title("🎯 Scout-X | Unified Dashboard")

# مدخلات البحث
col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("START FULL ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        with st.status("Gathering Intelligence...", expanded=True) as status:
            # 1. جلب البيانات الأساسية
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            time.sleep(1.5)
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            time.sleep(1.5)
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=20&api_key={API_KEY}").json()
            time.sleep(1.5)
            
            # 2. تحليل الماتشات (10 ماتشات)
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
            match_list = []
            lanes = []
            for mid in m_ids:
                time.sleep(0.7) # ثبات الداتا
                m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_data:
                    for p in m_data['info']['participants']:
                        if p['puuid'] == puuid:
                            lanes.append(p.get('individualPosition', 'UNKNOWN'))
                            dur = max(1, m_data['info'].get('gameDuration', 0)/60)
                            match_list.append({
                                'win': p['win'], 'champ': p['championName'], 
                                'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'gold': p['goldEarned'], 'cs_m': round(p['totalMinionsKilled']/dur, 1),
                                'vision': p.get('visionScore', 0)
                            })
            
            top_role = Counter(lanes).most_common(1)[0][0] if lanes else "UNKNOWN"
            status.update(label="Analysis Finished!", state="complete", expanded=False)

        # --- العرض في صفحة واحدة ---
        
        # 1. القسم العلوي (الإحصائيات)
        st.write("---")
        c1, c2, c3 = st.columns(3)
        wr = (sum(1 for m in match_list if m["win"])/len(match_list)*100) if match_list else 0
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{wr:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{top_role}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(match_list)}</h2></div>', unsafe_allow_html=True)

        # 2. الرانك والماستري (جنب بعض)
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            if isinstance(ranks, list) and len(ranks) > 0:
                for r in ranks: r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
            else: r_html += "• Unranked Player"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
        with b2:
            m_html = "<b>⭐ TOP 3 CHAMPIONS</b><hr>"
            for c in mastery[:3]:
                c_name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                m_html += f"• {c_name}: Level {c.get('championLevel')} ({c.get('championPoints'):,} pts)<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

        # 3. الماتش هيستوري (الصور والتقارير)
        st.write("---")
        st.subheader("🎮 Detailed Match History")
        for m in match_list:
            res_txt = "WIN" if m['win'] else "LOSS"
            res_clr = "#3fb950" if m['win'] else "#da3633"
            with st.expander(f"● {m['champ']} - {m['kda']} ({res_txt})"):
                col_img, col_rep = st.columns([1, 4])
                with col_img: st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['champ']}.png", width=90)
                with col_rep:
                    st.markdown(f"""
                        <div class="report-card">
                            <b style="color:{res_clr}">{res_txt} PERFORMANCE</b><br>
                            💰 Gold: {m['gold']:,} | 🎯 Farm: {m['cs_m']} CS/m | 👁️ Vision: {m['vision']}
                        </div>
                    """, unsafe_allow_html=True)

        # 4. بابلز الماستري (اللمسة النهائية المضحكة)
        st.write("---")
        st.subheader("🌌 Champion Mastery Cloud")
        if mastery:
            max_pts = mastery[0].get('championPoints', 1)
            cloud_html = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:20px; padding:20px; background:#161b22; border-radius:15px;">'
            for c in mastery:
                c_name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                pts = c.get('championPoints', 0)
                sz = 60 + (math.sqrt(pts) / math.sqrt(max_pts)) * 120
                cloud_html += f'''
                <div style="text-align:center;">
                    <img class="bubble-hero" src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{c_name}.png" 
                         style="width:{sz}px; height:{sz}px; border-radius:50%; border:2px solid #f2cc60;">
                    <p style="font-size:10px; margin-top:5px;">{pts:,}</p>
                </div>'''
            st.markdown(cloud_html + '</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("Error fetching data. Check Riot ID or API Key.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
