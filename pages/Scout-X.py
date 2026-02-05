import streamlit as st
import requests
import time # المكتبة المسؤولة عن الانتظار

st.set_page_config(page_title="Scout-X | Stable Web", layout="wide")

# تصميم النيون اللي بتحبه
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; }
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

st.title("🎯 Scout-X | Stable Edition")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("START STABLE ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        # 1. طلب الـ PUUID
        acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
        puuid = acc['puuid']
        
        # --- بداية نظام الانتظار (سيبه ياخد وقته) ---
        with st.status("Fetching Data Slowly to bypass API limits...", expanded=True) as status:
            st.write("Fetching Summoner ID...")
            time.sleep(1.2) # انتظار ثانية وبدأت
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            
            st.write("Fetching Ranks and Mastery...")
            time.sleep(1.2) # هدوء قبل الطلب التاني
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            
            st.write("Fetching Recent Matches...")
            time.sleep(1.2)
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

            match_list = []
            for mid in m_ids:
                time.sleep(0.5) # انتظار بسيط بين كل ماتش والتاني لضمان استقرار الجدول
                m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_data:
                    for p in m_data['info']['participants']:
                        if p['puuid'] == puuid:
                            match_list.append({
                                'CHAMPION': p['championName'],
                                'RESULT': "WIN" if p['win'] else "LOSS",
                                'KDA': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'GOLD': f"{p['goldEarned']:,}"
                            })
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # --- عرض النتائج بعد الانتظار ---
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{(sum(1 for m in match_list if m["RESULT"]=="WIN")/len(match_list)*100) if match_list else 0:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>TOP</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(match_list)}</h2></div>', unsafe_allow_html=True)

        st.write("---")
        st.subheader("Match History Table")
        st.table(match_list) # عرض الجدول اللي كان بيختفي

        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_txt = "<b>🏆 RANK STATUS</b><br>"
            if isinstance(ranks, list) and ranks:
                for r in ranks: r_txt += f"• {r.get('tier')} {r.get('rank')}<br>"
            else: r_txt += "• Unranked"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_txt}</div>', unsafe_allow_html=True)
        
        with b2:
            m_txt = "<b>⭐ TOP MASTERY</b><br>"
            if isinstance(mastery, list):
                for c in mastery:
                    name = CHAMPS_MAP.get(str(c.get('championId')), "New Champ")
                    m_txt += f"• {name}: Lvl {c.get('championLevel')}<br>"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_txt}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Synchronization Error. Riot API is being protective. Wait 10s.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
