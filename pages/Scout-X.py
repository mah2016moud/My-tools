import streamlit as st
import requests
import pandas as pd

# تصميم الواجهة النيون بالكامل
st.set_page_config(page_title="Scout-X Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    /* تصميم الدوائر الملونة */
    .circle-stat {
        border: 3px solid #3fb950; border-radius: 50%;
        width: 140px; height: 140px; display: flex;
        flex-direction: column; align-items: center;
        justify-content: center; margin: auto;
        background: #161b22; box-shadow: 0 0 15px rgba(63, 185, 80, 0.2);
    }
    .card-neon { border-radius: 15px; padding: 20px; background: #161b22; margin: 10px 0; }
    .win { color: #3fb950; font-weight: bold; }
    .loss { color: #da3633; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# تأكد من تجديد هذا المفتاح من developer.riotgames.com
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs()

st.title("🎯 Scout-X | Web Edition v5.0")

# صف البحث
c1, c2, c3 = st.columns([1, 3, 1])
with c1: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with c2: riot_id = st.text_input("Player Name#Tag", value="Saeed#1111")
with c3: 
    st.write(" ")
    analyze_btn = st.button("RUN ANALYSIS")

if analyze_btn:
    if "#" not in riot_id:
        st.warning("Please use the format: Name#Tag")
    else:
        name, tag = riot_id.split("#")
        mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
        plat, rout = mapping[region]

        with st.spinner('Synchronizing with Riot Servers...'):
            try:
                # 1. جلب الـ PUUID
                acc_url = f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}"
                acc_data = requests.get(acc_url).json()
                puuid = acc_data['puuid']

                # 2. جلب الـ Summoner ID (حل مشكلة 'id')
                sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
                s_id = sum_data.get('id')

                # 3. جلب الماتشات والرانك والمستري
                ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
                m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

                # معالجة البيانات
                match_results = []
                wins = 0
                for mid in m_ids:
                    m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                    for p in m_info['info']['participants']:
                        if p['puuid'] == puuid:
                            match_results.append(p)
                            if p['win']: wins += 1

                # --- العرض (الدوائر الثلاثة) ---
                st.write("### Live Performance Status")
                g1, g2, g3 = st.columns(3)
                with g1: st.markdown(f'<div class="circle-stat"><small>WIN RATE</small><h2>{(wins/len(m_ids))*100:.0f}%</h2></div>', unsafe_allow_html=True)
                with g2: st.markdown(f'<div class="circle-stat" style="border-color:#f2cc60"><small>MATCHES</small><h2>{len(m_ids)}</h2></div>', unsafe_allow_html=True)
                with g3: 
                    tier = ranks[0]['tier'] if ranks else "UNRANKED"
                    st.markdown(f'<div class="circle-stat" style="border-color:#58a6ff"><small>RANK</small><h4 style="margin:0">{tier}</h4></div>', unsafe_allow_html=True)

                # --- ريبورت كل جيم ---
                st.write("---")
                st.subheader("Match History Reports")
                for p in match_results:
                    color = "#3fb950" if p['win'] else "#da3633"
                    with st.expander(f"🎮 {p['championName']} - {'WIN' if p['win'] else 'LOSS'} ({p['kills']}/{p['deaths']}/{p['assists']})"):
                        st.markdown(f"""
                        <div style="border-left: 5px solid {color}; padding-left:15px">
                            <b>Status:</b> {'Victory' if p['win'] else 'Defeat'}<br>
                            <b>Gold Earned:</b> {p['goldEarned']:,} | <b>Vision Score:</b> {p.get('visionScore', 0)}<br>
                            <b>Damage to Champs:</b> {p['totalDamageDealtToChampions']:,}
                        </div>
                        """, unsafe_allow_html=True)

                # --- التوب 3 شامبيون (التي طلبتها) ---
                st.write("---")
                st.subheader("⭐ Top 3 Champions (Mastery)")
                tm1, tm2, tm3 = st.columns(3)
                cols = [tm1, tm2, tm3]
                for i, m in enumerate(mastery):
                    with cols[i]:
                        c_name = CHAMPS_MAP.get(str(m['championId']), 'Unknown')
                        st.markdown(f"""
                        <div class="card-neon" style="border: 1px solid #f2cc60; text-align:center">
                            <img src="https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{c_name}.png" width="70" style="border-radius:50%"><br>
                            <b>{c_name}</b><br>Level {m['championLevel']}<br><small>{m['championPoints']:,} pts</small>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Synchronization Error: {str(e)}. Check your API Key!")

st.divider()
st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
