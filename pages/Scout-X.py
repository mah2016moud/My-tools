import streamlit as st
import requests

# 1. إعدادات التصميم (النيون والدوائر)
st.set_page_config(page_title="Scout-X | Final Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 50%; width: 140px; height: 140px; text-align: center; margin: auto; }
    .card-rank { background: #161b22; border: 2px solid #00d4ff; border-radius: 12px; padding: 20px; height: 220px; }
    .card-mastery { background: #161b22; border: 2px solid #f2cc60; border-radius: 12px; padding: 20px; height: 220px; }
    .report-box { background: #0d1117; border: 1px solid #58a6ff; padding: 15px; border-radius: 10px; margin-top: 10px; }
    .mastery-list { list-style-type: disc; padding-left: 20px; font-size: 18px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# الـ API KEY - (تأكد من تجديده من موقع Riot)
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        # هنا السر: تحويل المفتاح لنص لضمان المطابقة
        return {str(v['key']): v['name'] for v in r['data'].values()}
    except: return {}

CHAMPS_MAP = get_champs_map()

st.title("🎯 Scout-X | Master Web Edition")

# واجهة البحث (سيرفر + اسم)
col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id:
    riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn:
    st.write(" ")
    analyze_btn = st.button("RUN ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    with st.spinner('Synchronizing System Data...'):
        try:
            # 1. طلبات الـ API
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            
            sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_data.get('id')
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

            # 2. معالجة الدوائر العلوية (Stats)
            match_list, roles, wins = [], [], 0
            for mid in m_ids:
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                for p in m_info['info']['participants']:
                    if p['puuid'] == puuid:
                        res = "WIN" if p['win'] else "LOSS"
                        if p['win']: wins += 1
                        roles.append(p.get('individualPosition', 'UNKNOWN'))
                        match_list.append({
                            "CHAMP": p['championName'], "RES": res, 
                            "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                            "GOLD": p['goldEarned'], "FARM": p['totalMinionsKilled'], "VIS": p.get('visionScore', 0)
                        })

            # عرض الدوائر
            st.write("---")
            g1, g2, g3 = st.columns(3)
            with g1: st.markdown(f'<div class="stMetric"><p>WIN RATE</p><h3>{(wins/len(m_ids))*100:.0f}%</h3></div>', unsafe_allow_html=True)
            with g2: 
                top_role = max(set(roles), key=roles.count) if roles else "N/A"
                st.markdown(f'<div class="stMetric" style="border-color:#f2cc60"><p>TOP ROLE</p><h3>{top_role}</h3></div>', unsafe_allow_html=True)
            with g3: st.markdown(f'<div class="stMetric" style="border-color:#58a6ff"><p>MATCHES</p><h3>{len(m_ids)}</h3></div>', unsafe_allow_html=True)

            # 3. عرض الماتشات (Match History)
            st.subheader("Match History Reports")
            for m in match_list:
                with st.expander(f"🎮 {m['CHAMP']} - {m['RES']} ({m['KDA']})"):
                    col_img, col_rep = st.columns([1, 4])
                    with col_img: st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['CHAMP']}.png", width=70)
                    with col_rep: st.markdown(f'<div class="report-box"><b style="color:{"#3fb950" if m["RES"]=="WIN" else "#da3633"}">{m["RES"]} REPORT</b><br>💰 Gold: {m["GOLD"]:,} | 🎯 Farm: {m["FARM"]} | 👁️ Vision: {m["VIS"]}</div>', unsafe_allow_html=True)

            # 4. المربعات السفلية (الرانك والمستري - المطابقة للكمبيوتر)
            st.write("---")
            b1, b2 = st.columns(2)
            with b1:
                rank_txt = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "UNRANKED"
                st.markdown(f'<div class="card-rank"><h3 style="color:#00d4ff">🏆 RANK DATA</h3><br><h2 style="color:white">{rank_txt}</h2></div>', unsafe_allow_html=True)
            
            with b2:
                # القائمة النصية للأبطال
                m_items = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Unknown')}: Lvl {c['championLevel']}</li>" for c in mastery])
                st.markdown(f"""
                    <div class="card-mastery">
                        <div style="color:#f2cc60; font-size:24px; font-weight:bold; margin-bottom:15px;">⭐ TOP MASTERY</div>
                        <ul class="mastery-list">{m_items}</ul>
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error("Riot API Throttled: Please check your API Key or wait 10 seconds.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
