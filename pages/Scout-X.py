import streamlit as st
import requests
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Scout-X Web", layout="wide")

# تصميم الـ CSS لضمان الشكل المظبوط
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .card { background: #161b22; border-radius: 10px; padding: 20px; border: 1px solid #30363d; height: 100%; }
    .win-text { color: #3fb950; font-weight: bold; }
    .loss-text { color: #da3633; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# استبدل هذا المفتاح دائماً إذا انتهت صلاحيته
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs()

st.title("🎯 Scout-X | Web Edition")

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col2:
    riot_id = st.text_input("Player ID (Name#Tag)", placeholder="Saeed#1111")
with col3:
    st.write(" ") 
    analyze_btn = st.button("ANALYZE SUBJECT")

if analyze_btn:
    if "#" not in riot_id:
        st.warning("Please enter ID in Name#Tag format.")
    else:
        name, tag = riot_id.split("#")
        mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
        plat, rout = mapping[region]

        with st.spinner('Fetching live data from Riot servers...'):
            try:
                # 1. Account Data
                acc_url = f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}"
                acc_req = requests.get(acc_url)
                if acc_req.status_code != 200:
                    st.error(f"Account not found or API Key expired (Error {acc_req.status_code})")
                else:
                    puuid = acc_req.json()['puuid']
                    
                    # 2. Summoner & Rank
                    sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
                    s_id = sum_res['id']
                    ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                    
                    # 3. Match History
                    m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
                    
                    matches_data = []
                    wins = 0
                    for mid in m_ids:
                        m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                        for p in m_info['info']['participants']:
                            if p['puuid'] == puuid:
                                matches_data.append({
                                    "CHAMP": p['championName'],
                                    "RESULT": "WIN" if p['win'] else "LOSS",
                                    "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                    "GOLD": p['goldEarned']
                                })
                                if p['win']: wins += 1

                    # عرض النتائج
                    m1, m2, m3 = st.columns(3)
                    m1.metric("WIN RATE", f"{(wins/len(m_ids))*100:.0f}%" if m_ids else "0%")
                    m2.metric("LAST 10 MATCHES", len(m_ids))
                    m3.metric("CURRENT TIER", ranks[0]['tier'] if ranks else "Unranked")

                    # الجدول
                    st.subheader("Match History Analysis")
                    df = pd.DataFrame(matches_data)
                    st.table(df.style.applymap(lambda v: 'color: #3fb950' if v == 'WIN' else 'color: #da3633', subset=['RESULT']))

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

st.divider()
st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
