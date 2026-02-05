import streamlit as st
import requests
import pandas as pd

# 1. إعدادات الصفحة والتصميم النيون المطابق لنسخة الكمبيوتر
st.set_page_config(page_title="Scout-X | Web Edition", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stTable { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    /* ستايل المربعات الملونة زي نسخة الكمبيوتر */
    .rank-box { background: #161b22; border: 2px solid #00d4ff; border-radius: 12px; padding: 20px; min-height: 160px; }
    .mastery-box { background: #161b22; border: 2px solid #f2cc60; border-radius: 12px; padding: 20px; min-height: 160px; }
    .win-text { color: #3fb950 !important; font-weight: bold; }
    .loss-text { color: #da3633 !important; font-weight: bold; }
    .stButton>button { background-color: #238636; color: white; width: 100%; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# الـ API KEY - تأكد من تحديثه دائماً
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs_map()

# الواجهة العلوية
st.title("🎯 Scout-X | Master Edition v4.0")

top_col1, top_col2, top_col3 = st.columns([1, 4, 1])
with top_col1:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with top_col2:
    riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with top_col3:
    st.write(" ")
    analyze_btn = st.button("ANALYZE")

if analyze_btn:
    if "#" not in riot_id:
        st.error("Please use Name#Tag format.")
    else:
        name, tag = riot_id.split("#")
        mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
        plat, rout = mapping[region]

        with st.spinner('Accessing Riot Live Servers...'):
            try:
                # حل مشكلة الـ 'id' بخطوات منظمة
                acc_req = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}")
                if acc_req.status_code != 200:
                    st.error(f"Error: Account not found or API Key expired (Code: {acc_req.status_code})")
                else:
                    puuid = acc_req.json()['puuid']
                    
                    # جلب بيانات Summoner و Rank
                    sum_data = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
                    s_id = sum_data.get('id')
                    
                    ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                    mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
                    m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

                    # معالجة الماتشات للجدول
                    match_list = []
                    wins, total_kda = 0, 0
                    for mid in m_ids:
                        m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                        for p in m_info['info']['participants']:
                            if p['puuid'] == puuid:
                                res = "WIN" if p['win'] else "LOSS"
                                if p['win']: wins += 1
                                match_list.append({
                                    "CHAMPION": p['championName'],
                                    "RESULT": res,
                                    "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                    "GOLD": f"{p['goldEarned']:,}"
                                })

                    # عرض الـ Gauges/Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("WIN RATE", f"{(wins/len(m_ids))*100:.0f}%")
                    m2.metric("TOP ROLE", "Determining...")
                    m3.metric("MATCHES", len(m_ids))

                    # الجدول بالألوان الأصلية
                    st.subheader("Match History")
                    df = pd.DataFrame(match_list)
                    
                    def color_result(val):
                        color = '#3fb950' if val == "WIN" else '#da3633'
                        return f'color: {color}; font-weight: bold'

                    st.table(df.style.applymap(color_result, subset=['RESULT']))

                    # المربعات السفلية المتوازنة
                    st.divider()
                    b1, b2 = st.columns(2)
                    with b1:
                        rank_txt = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "UNRANKED"
                        st.markdown(f'<div class="rank-box"><h3 style="color:#00d4ff">🏆 PLAYER RANK</h3><br><b>{rank_txt}</b></div>', unsafe_allow_html=True)
                    with b2:
                        m_txt = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Unknown')}: Lvl {c['championLevel']}</li>" for c in mastery])
                        st.markdown(f'<div class="mastery-box"><h3 style="color:#f2cc60">⭐ TOP MASTERY</h3><br><ul>{m_txt}</ul></div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"System Error: {str(e)}")

# الحقوق في الأسفل تماماً
st.divider()
st.markdown('<p style="text-align: center; color: #8b949e;">© 2026 | Developed by MAHMOUD ABDALLA</p>', unsafe_allow_html=True)
