import streamlit as st
import requests
import time

st.set_page_config(page_title="Scout-X | Final Edition v4.0", layout="wide")

# تصميم النيون اللي في شغلك
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .neon-box { border: 2px solid #3fb950; border-radius: 40px; padding: 20px; text-align: center; background: #161b22; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; border: 2px solid; min-height: 180px; }
    .report-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
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

st.title("🎯 Scout-X | Final Edition v4.0")

col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv: region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id: riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn: 
    st.write(" ")
    analyze_btn = st.button("RUN DEEP ANALYSIS")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    try:
        # نظام الانتظار المطول لضمان الرانك والماستري
        with st.status("Performing Deep Sync (Please wait 20-30s)...", expanded=True) as status:
            # 1. جلب PUUID
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc['puuid']
            time.sleep(2.0) # انتظار طويل لراحة السيرفر
            
            # 2. جلب Summoner ID والرانك (هنا المشكلة كانت بتحصل)
            st.write("📡 Synchronizing Rank Data...")
            sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
            s_id = sum_res.get('id')
            time.sleep(2.0) 
            
            ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
            st.write("✅ Rank Data Secured.")
            time.sleep(2.0)
            
            # 3. جلب التوب شامبيونز
            st.write("⭐ Fetching Mastery Records...")
            mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
            time.sleep(2.0)
            
            # 4. جلب الماتشات والتقارير
            st.write("🎮 Analyzing Last 10 Matches...")
            m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

            match_list = []
            for mid in m_ids:
                time.sleep(1.0) # نص ثانية لضمان جودة الريبورت
                m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                if 'info' in m_data:
                    for p in m_data['info']['participants']:
                        if p['puuid'] == puuid:
                            dur = max(1, m_data['info'].get('gameDuration', 0)/60)
                            cs_m = p['totalMinionsKilled'] / dur
                            match_list.append({
                                'win': p['win'], 'champ': p['championName'], 
                                'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'gold': p['goldEarned'], 'cs': p['totalMinionsKilled'], 'cs_m': round(cs_m, 1),
                                'vision': p.get('visionScore', 0), 'time': round(dur, 1),
                                'g_rate': "GODLIKE" if p['goldEarned'] > 16000 else "GREAT" if p['goldEarned'] > 12000 else "DECENT" if p['goldEarned'] > 8000 else "BAD",
                                'f_rate': "GODLIKE" if cs_m > 8.5 else "GREAT" if cs_m > 6.5 else "DECENT" if cs_m > 4.5 else "BAD",
                                'v_rate': "GODLIKE" if p.get('visionScore', 0) > 35 else "GREAT" if p.get('visionScore', 0) > 25 else "DECENT" if p.get('visionScore', 0) > 15 else "BAD"
                            })
            status.update(label="Analysis Complete! Displaying results...", state="complete", expanded=False)

        # --- العرض النهائي ---
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="neon-box" style="border-color:#3fb950"><p>WIN RATE</p><h2>{(sum(1 for m in match_list if m["win"])/len(match_list)*100) if match_list else 0:.0f}%</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="neon-box" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>TOP</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="neon-box" style="border-color:#58a6ff"><p>MATCHES</p><h2>{len(match_list)}</h2></div>', unsafe_allow_html=True)

        # المربعات السفلية (الرانك والماستري)
        st.write("---")
        b1, b2 = st.columns(2)
        with b1:
            r_html = "<b>🏆 RANK STATUS</b><hr>"
            if isinstance(ranks, list) and len(ranks) > 0:
                for r in ranks: r_html += f"• <b>{r.get('tier')} {r.get('rank')}</b> ({r.get('leaguePoints')} LP)<br>"
            else: r_html += "• Player is currently Unranked"
            st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
        
        with b2:
            m_html = "<b>⭐ TOP MASTERY</b><hr>"
            if isinstance(mastery, list) and len(mastery) > 0:
                for c in mastery:
                    c_name = CHAMPS_MAP.get(str(c.get('championId')), "New Champ")
                    m_html += f"• <b>{c_name}</b>: Level {c.get('championLevel')} ({c.get('championPoints'):,} pts)<br>"
            else: m_html += "• Mastery data not available"
            st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

        st.write("---")
        st.subheader("Detailed Performance Reports")
        for m in match_list:
            res_txt = "WIN" if m['win'] else "LOSS"
            res_clr = "#3fb950" if m['win'] else "#da3633"
            with st.expander(f"🎮 {m['champ']} - {m['kda']} ({res_txt})"):
                col_img, col_rep = st.columns([1, 4])
                with col_img: st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['champ']}.png", width=100)
                with col_rep:
                    def get_c(r): return "#3fb950" if r == "GODLIKE" else "#58a6ff" if r == "GREAT" else "#f2cc60" if r == "DECENT" else "#da3633"
                    st.markdown(f"""
                        <div class="report-card">
                            <h3 style="color:{res_clr}">{res_txt} REPORT</h3>
                            💰 <b>Gold:</b> {m['gold']:,} <span style="color:{get_c(m['g_rate'])}">[{m['g_rate']}]</span><br>
                            🎯 <b>Farm:</b> {m['cs']} ({m['cs_m']} CS/m) <span style="color:{get_c(m['f_rate'])}">[{m['f_rate']}]</span><br>
                            👁️ <b>Vision:</b> {m['vision']} <span style="color:{get_c(m['v_rate'])}">[{m['v_rate']}]</span><br>
                            ⏱️ <b>Time:</b> {m['time']} min
                        </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Sync Interrupted: Riot servers are busy. Please try again in 10 seconds.")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
