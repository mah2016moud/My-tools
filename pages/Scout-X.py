import streamlit as st
import requests
import pandas as pd

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="Scout-X Web", layout="wide")

# تخصيص التصميم ليكون مطابقاً لنسخة الـ Desktop الأصلية
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    div[data-testid="stMetricValue"] { color: #58a6ff; font-size: 24px; }
    .stTable { background-color: #161b22; border-radius: 10px; }
    .win-text { color: #3fb950; font-weight: bold; }
    .loss-text { color: #da3633; font-weight: bold; }
    .card { background: #161b22; border-radius: 10px; padding: 20px; margin: 10px 0; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

def get_champs():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {v['key']: v['name'] for k, v in r['data'].items()}
    except: return {}

CHAMPS_MAP = get_champs()

st.title("🎯 Scout-X | Web Edition")

# واجهة البحث المنظمة
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col2:
    riot_id = st.text_input("Player ID", placeholder="Name#Tag")
with col3:
    st.write(" ") # لضبط المحاذاة
    analyze_btn = st.button("ANALYZE SUBJECT")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    mapping = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = mapping[region]

    with st.spinner('Analyzing Match History...'):
        try:
            # طلبات الـ API الأساسية
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res['id']
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

            # معالجة بيانات الماتشات والدوائر (Gauges)
            matches_data = []
            wins = 0
            for mid in m_ids:
                m_info = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                for p in m_info['info']['participants']:
                    if p['puuid'] == puuid:
                        is_win = p['win']
                        if is_win: wins += 1
                        matches_data.append({
                            "CHAMPION": p['championName'],
                            "RESULT": "WIN" if is_win else "LOSS",
                            "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
                            "GOLD": f"{p['goldEarned']:,}"
                        })

            # عرض الدوائر (Metrics)
            m1, m2, m3 = st.columns(3)
            m1.metric("WIN RATE", f"{(wins/len(m_ids))*100:.0f}%")
            m2.metric("MATCHES", len(m_ids))
            m3.metric("AVG KDA", "Stable")

            # عرض الجدول مع تلوين النتائج
            st.subheader("Match History")
            df = pd.DataFrame(matches_data)
            
            def style_result(val):
                color = '#3fb950' if val == 'WIN' else '#da3633'
                return f'color: {color}; font-weight: bold'

            st.table(df.style.applymap(style_result, subset=['RESULT']))

            # المربعات السفلية (الرانك والمستري)
            st.divider()
            b1, b2 = st.columns(2)
            with b1:
                rank_info = f"{ranks[0]['tier']} {ranks[0]['rank']}" if ranks else "Unranked"
                st.markdown(f'<div class="card"><h3 style="color:#00d4ff">🏆 RANK</h3>{rank_info}</div>', unsafe_allow_html=True)
            with b2:
                m_html = "".join([f"<li>{CHAMPS_MAP.get(str(c['championId']), 'Unknown')}: Lvl {c['championLevel']}</li>" for c in mastery])
                st.markdown(f'<div class="card"><h3 style="color:#f2cc60">⭐ TOP MASTERY</h3><ul>{m_html}</ul></div>', unsafe_allow_html=True)

            # حقوق المطور في الويب
            st.caption("© 2026 | Developed by MAHMOUD ABDALLA")

        except Exception as e:
            st.error("Player data not found. Please check Name#Tag and Region.")
