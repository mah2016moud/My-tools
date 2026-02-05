import streamlit as st
import requests
import time
import math
from collections import Counter

# إعدادات الصفحة والتصميم النيون
st.set_page_config(page_title="Scout-X | Final Edition v4.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 180px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    /* أنيميشن بسيط للدواير */
    .champ-circle { transition: transform 0.3s, box-shadow 0.3s; cursor: pointer; }
    .champ-circle:hover { transform: scale(1.1); box-shadow: 0 0 20px rgba(242, 204, 96, 0.8); }
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

# القائمة الجانبية للتنقل بين الصفحات
page = st.sidebar.radio("Navigate", ["Player Scout", "Mastery Cloud"])

st.title("🎯 Scout-X | Final Edition v4.0")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("RUN DEEP ANALYSIS")

# استخدام Session State لحفظ البيانات عشان ما تروحش لما تنقل بين الصفحات
if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        with st.status("Performing Deep Sync (Wait ~25s for stability)...", expanded=True) as status:
            # 1. جلب PUUID
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            st.session_state.puuid = acc['puuid']
            time.sleep(2.0)
            
            # 2. جلب الرانك والماستري (بثبات عالي)
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{st.session_state.puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            time.sleep(2.0) 
            
            st.session_state.ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            time.sleep(2.0)
            st.session_state.mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{st.session_state.puuid}/top?count=15&api_key={API_KEY}").json()
            time.sleep(2.0)
            
            # 3. تحليل الماتشات والـ Lane الحقيقي
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{st.session_state.puuid}/ids?count=10&api_key={API_KEY}").json()
            match_list = []
            lanes_played = []
            for mid in m_ids:
                time.sleep(1.0) 
                m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_data:
                    for p in m_data['info']['participants']:
                        if p['puuid'] == st.session_state.puuid:
                            lane = p.get('individualPosition', 'UNKNOWN')
                            if lane in ['NONE', '', 'UNKNOWN']: lane = p.get('lane', 'UNKNOWN')
                            lanes_played.append(lane)
                            dur = max(1, m_data['info'].get('gameDuration', 0)/60)
                            cs_m = p['totalMinionsKilled'] / dur
                            match_list.append({
                                'win': p['win'], 'champ': p['championName'], 'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'gold': p['goldEarned'], 'cs': p['totalMinionsKilled'], 'cs_m': round(cs_m, 1),
                                'vision': p.get('visionScore', 0), 'time': round(dur, 1),
                                'g_rate': "GODLIKE" if p['goldEarned'] > 16000 else "GREAT" if p['goldEarned'] > 12000 else "DECENT",
                                'f_rate': "GODLIKE" if cs_m > 8.5 else "GREAT" if cs_m > 6.5 else "DECENT",
                                'v_rate': "GODLIKE" if p.get('visionScore', 0) > 35 else "GREAT" if p.get('visionScore', 0) > 25 else "DECENT"
                            })
            st.session_state.match_list = match_list
            st.session_state.top_role = Counter(lanes_played).most_common(1)[0][0] if lanes_played else "UNKNOWN"
            status.update(label="Deep Analysis Complete!", state="complete", expanded=False)
    except: st.error("Error connecting to Riot. Check API Key.")

# --- منطق عرض الصفحات ---
if "puuid" in st.session_state:
    if page == "Player Scout":
        # عرض الإحصائيات العلوية
        c1, c2, c3 = st.columns(3)
        win_rate = (sum(1 for m in st.session_state.match_list if m["win"])/len(st.session_state.match_list)*100)
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{win_rate:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{st.session_state.top_role}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(st.session_state.match_list)}</h2></div>', unsafe_allow_html=True)

        # الرانك والماستري
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            for r in st.session_state.ranks: r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html if st.session_state.ranks else "Unranked"}</div>', unsafe_allow_html=True)
        with b2:
            m_html = "<b>⭐ TOP MASTERY</b><hr>"
            for c in st.session_state.mastery[:3]:
                name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
                m_html += f"• {name}: Level {c.get('championLevel')}<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

        # ريبورتات الماتشات
        st.write("---")
        st.subheader("Match Performance Reports")
        for m in st.session_state.match_list:
            res_clr = "#3fb950" if m['win'] else "#da3633"
            with st.expander(f"🎮 {m['champ']} - {m['kda']}"):
                col1, col2 = st.columns([1, 4])
                with col1: st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['champ']}.png", width=100)
                with col2:
                    st.markdown(f'<div class="report-card"><h3 style="color:{res_clr}">REPORT</h3>'
                                f'💰 Gold: {m["gold"]:,} <b>[{m["g_rate"]}]</b><br>'
                                f'🎯 Farm: {m["cs_m"]} CS/m <b>[{m["f_rate"]}]</b><br>'
                                f'👁️ Vision: {m["vision"]} <b>[{m["v_rate"]}]</b></div>', unsafe_allow_html=True)

    elif page == "Mastery Cloud":
        st.header("🌌 Champion Mastery Cloud")
        st.caption("أكبر الدوائر تمثل الأبطال الأكثر لعباً واحترافاً")
        
        cloud_html = '<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 20px; padding: 30px; background: #0d1117; border-radius: 20px;">'
        max_pts = st.session_state.mastery[0].get('championPoints', 1)
        
        for c in st.session_state.mastery:
            c_name = CHAMPS_MAP.get(str(c.get('championId')), "Hero")
            pts = c.get('championPoints', 0)
            size = 60 + (math.sqrt(pts) / math.sqrt(max_pts)) * 140 # معادلة الحجم
            
            cloud_html += f'''
            <div style="text-align: center;">
                <img class="champ-circle" src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{c_name}.png" 
                     style="width: {size}px; height: {size}px; border-radius: 50%; border: 3px solid #f2cc60;"
                     title="{c_name}: {pts:,} pts">
                <p style="margin-top: 5px; font-size: 11px;">{c_name}</p>
            </div>'''
        cloud_html += '</div>'
        st.markdown(cloud_html, unsafe_allow_html=True)

st.sidebar.caption("© 2026 | Developed by MAHMOUD ABDALLA")
