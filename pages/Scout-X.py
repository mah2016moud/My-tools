import streamlit as st
import requests

st.set_page_config(page_title="Scout-X | Final Fix", layout="wide")

# 1. جلب البيانات وتحويل الـ Keys لنصوص فوراً لحل مشكلة الـ ID
@st.cache_data(ttl=3600)
def get_champs_dict():
    try:
        data = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {str(v['key']): v['name'] for v in data['data'].values()}
    except: return {}

CHAMPS_MAP = get_champs_dict()
API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

st.title("🎯 Scout-X | Web Edition")

# واجهة البحث
col1, col2 = st.columns([3, 1])
with col1: riot_id = st.text_input("Name#Tag")
with col2: analyze = st.button("ANALYZE")

if analyze and "#" in riot_id:
    name, tag = riot_id.split("#")
    try:
        # طلب الـ PUUID (الأساس)
        acc = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
        puuid = acc['puuid']
        
        # طلب الـ Mastery بشكل منفصل تماماً
        mastery_url = f"https://eun1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}"
        mastery_data = requests.get(mastery_url).json()

        st.write("---")
        # عرض الـ Mastery فوراً في الأعلى عشان نضمن ظهورها
        m_col1, m_col2 = st.columns(2)
        
        with m_col2: # مربع الـ Mastery
            st.markdown('<div style="border:2px solid #f2cc60; padding:20px; border-radius:15px; background:#161b22">', unsafe_allow_html=True)
            st.subheader("⭐ TOP MASTERY")
            if isinstance(mastery_data, list):
                for champ in mastery_data:
                    c_name = CHAMPS_MAP.get(str(champ['championId']), "New Champion")
                    st.write(f"🔹 **{c_name}**: Level {champ['championLevel']}")
            else:
                st.warning("Mastery Data currently throttled by API.")
            st.markdown('</div>', unsafe_allow_html=True)

        with m_col1: # مربع الرانك
            st.markdown('<div style="border:2px solid #00d4ff; padding:20px; border-radius:15px; background:#161b22">', unsafe_allow_html=True)
            st.subheader("🏆 RANK STATUS")
            st.write("Rank data is being synchronized...")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("Riot API is busy. Please wait 10 seconds and try again.")
