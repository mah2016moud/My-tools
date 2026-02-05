import streamlit as st
import requests
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Scout-X Web", layout="wide")

# ستايل CSS مخصص للحفاظ على شكل الـ Neon والـ Cards اللي بتحبها
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background-color: #238636; color: white; border-radius: 5px; width: 100%; }
    .rank-card { border: 2px solid #00d4ff; border-radius: 10px; padding: 20px; background: #161b22; }
    .mastery-card { border: 2px solid #f2cc60; border-radius: 10px; padding: 20px; background: #161b22; }
    .win { color: #3fb950; font-weight: bold; }
    .loss { color: #da3633; font-weight: bold; }
    </style>
    """, unsafe_allow_header_ some_attrs=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

def get_champs():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs()

st.title("🎯 Scout-X | Web Edition")

# البحث
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col2:
    riot_id = st.text_input("Enter ID (Name#Tag)", placeholder="Mahmoud#EUNE")
with col3:
    analyze_btn = st.button("ANALYZE")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    with st.spinner('Fetching Data...'):
        try:
            # جلب البيانات
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res['id']
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()
            
            # عرض الجدول
            matches_data = []
            for mid in m_ids:
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                for p in m_info['info']['participants']:
                    if p['puuid'] == puuid:
                        matches_data.append({
                            "CHAMPION": p['championName'],
                            "RESULT": "WIN" if p['win'] else "LOSS",
                            "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                            "GOLD": f"{p['goldEarned']:,}"
                        })

            st.subheader("Recent Matches")
            df = pd.DataFrame(matches_data)
            # تلوين الجدول في Streamlit
            def color_result(val):
                color = '#3fb950' if val == 'WIN' else '#da3633'
                return f'color: {color}'
            st.table(df.style.applymap(color_result, subset=['RESULT']))

            # المربعات السفلية (الرانك والمستري)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="rank-card"><h3>🏆 RANK</h3>{ranks[0]['tier']+' '+ranks[0]['rank'] if ranks else 'Unranked'}</div>""", unsafe_allow_html=True)
            with c2:
                m_list = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Unknown')}: Lvl {c['championLevel']}</li>" for c in mastery])
                st.markdown(f"""<div class="mastery-card"><h3>⭐ MASTERY</h3><ul>{m_list}</ul></div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")