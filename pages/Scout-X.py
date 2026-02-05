import streamlit as st
import requests

# 1. إعدادات التصميم (النيون)
st.set_page_config(page_title="Scout-X | Web Master", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 50%; width: 140px; height: 140px; text-align: center; margin: auto; }
    .card-style { background: #161b22; border: 2px solid #f2cc60; border-radius: 12px; padding: 20px; min-height: 200px; }
    .mastery-text { font-size: 18px; color: #f2cc60; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# الـ API KEY - (تأكد إنه شغال من الموقع)
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs_map()

st.title("🎯 Scout-X | Master Web Edition")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn:
    st.write(" ")
    analyze_btn = st.button("RUN ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    try:
        # 1. جلب البيانات
        acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
        puuid = acc['puuid']
        sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
        s_id = sum_data.get('id')
        
        ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
        mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
        m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

        # 2. عرض المربعات السفلية (الرانك والمستري) أولاً لضمان ظهورها
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            rank_txt = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "UNRANKED"
            st.markdown(f'<div class="card-style" style="border-color:#00d4ff"><h3>🏆 RANK</h3><h2>{rank_txt}</h2></div>', unsafe_allow_html=True)
        with b2:
            # القائمة النصية المطابقة للكمبيوتر
            m_list = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Unknown')}: Lvl {c['championLevel']}</li>" for c in mastery])
            st.markdown(f'<div class="card-style"><div class="mastery-text">⭐ TOP MASTERY</div><ul>{m_list}</ul></div>', unsafe_allow_html=True)

        # 3. عرض الماتشات (اللي كانت شغالة تمام)
        st.write("---")
        st.subheader("Match History Reports")
        for mid in m_ids:
            m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
            for p in m_info['info']['participants']:
                if p['puuid'] == puuid:
                    with st.expander(f"🎮 {p['championName']} - {'WIN' if p['win'] else 'LOSS'} ({p['kills']}/{p['deaths']}/{p['assists']})"):
                        st.write(f"💰 Gold: {p['goldEarned']} | 🎯 Farm: {p['totalMinionsKilled']}")

    except Exception as e:
        st.error("Connection Error: Please refresh the page or check API Key.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
