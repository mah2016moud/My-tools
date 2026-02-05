import streamlit as st
import requests

# 1. إعدادات الصفحة والتصميم الفخم (نفس ألوان نسخة PyQt6)
st.set_page_config(page_title="Scout-X | Final Edition v4.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }
    .stMetric { background: #161b22; border: 2px solid #30363d; padding: 20px; border-radius: 72px; text-align: center; }
    .neon-gauge { border: 2px solid #00d4ff; border-radius: 72px; padding: 20px; text-align: center; background: #161b22; min-height: 140px; }
    .card-bot { background: #161b22; border-radius: 12px; padding: 15px; min-height: 170px; border: 2px solid; }
    .report-win { color: #3fb950; font-weight: bold; }
    .report-loss { color: #da3633; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "RGAPI-4b0b55ed-8c7c-423d-bb3e-d6a6eb060c7d"

# 2. جلب خريطة الأبطال (نفس منطق نسخة الكمبيوتر)
@st.cache_data(ttl=3600)
def get_champs_map():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json").json()
        return {str(v['key']): v['name'] for v in r['data'].values()}
    except: return {}

CHAMPS_MAP = get_champs_map()

st.title("🎯 Scout-X | Final Edition v4.0")

# 3. واجهة المدخلات
col_srv, col_id, col_btn = st.columns([1, 3, 1])
with col_srv:
    region = st.selectbox("Region", ["EUNE", "EUW", "NA"])
with col_id:
    riot_id = st.text_input("Name#Tag", placeholder="Saeed#1111")
with col_btn:
    st.write(" ")
    analyze_btn = st.button("ANALYZE SYSTEM")

if analyze_btn and "#" in riot_id:
    name, tag = riot_id.split("#")
    m_ = {"EUNE": ("eun1", "europe"), "EUW": ("euw1", "europe"), "NA": ("na1", "americas")}
    plat, rout = m_[region]

    with st.spinner('Running Analysis...'):
        try:
            # تنفيذ منطق الـ DataWorker
            acc = requests.get(f"https://{rout}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}").json()
            puuid = acc.get('puuid')
            
            if not puuid:
                st.error("Subject Missing (Check Name#Tag)")
            else:
                sum_res = requests.get(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}").json()
                s_id = sum_res.get('id')
                
                # جلب الرانك والمستري والماتشات
                ranks = requests.get(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}?api_key={API_KEY}").json()
                mastery = requests.get(f"https://{plat}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3&api_key={API_KEY}").json()
                m_ids = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=10&api_key={API_KEY}").json()

                match_list = []
                for mid in m_ids:
                    m_data = requests.get(f"https://{rout}.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={API_KEY}").json()
                    info = m_data.get('info', {})
                    for p in info.get('participants', []):
                        if p['puuid'] == puuid:
                            dur = max(1, info.get('gameDuration', 0)/60)
                            cs_m = p['totalMinionsKilled'] / dur
                            v_s = p.get('visionScore', 0)
                            gold = p['goldEarned']
                            
                            # نفس تقييمات نسخة الكمبيوتر بالظبط
                            match_list.append({
                                'win': p['win'], 'champ': p['championName'], 
                                'kda': f"{p['kills']}/{p['deaths']}/{p['assists']}",
                                'kda_val': round((p['kills'] + p['assists']) / max(1, p['deaths']), 2),
                                'gold': gold, 'cs': p['totalMinionsKilled'], 'cs_m': round(cs_m, 1),
                                'vision': v_s, 'time': round(dur, 1), 'lane': p.get('individualPosition', 'UNKNOWN'),
                                'g_rate': "GODLIKE" if gold > 16000 else "GREAT" if gold > 12000 else "DECENT" if gold > 8000 else "BAD",
                                'f_rate': "GODLIKE" if cs_m > 8.5 else "GREAT" if cs_m > 6.5 else "DECENT" if cs_m > 4.5 else "BAD",
                                'v_rate': "GODLIKE" if v_s > 35 else "GREAT" if v_s > 25 else "DECENT" if v_s > 15 else "BAD"
                            })

                # --- العرض (Dashboard) ---
                
                # 1. الدوائر (Neon Gauges)
                wr = (sum(1 for m in match_list if m['win']) / len(match_list) * 100) if match_list else 0
                avg_kda = sum(m['kda_val'] for m in match_list) / len(match_list) if match_list else 0
                lanes = [m['lane'] for m in match_list if m['lane'] not in ['UNKNOWN', 'None', '']]
                top_lane = max(set(lanes), key=lanes.count) if lanes else "N/A"

                st.write("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="neon-gauge" style="border-color:#3fb950"><p>WIN RATE</p><h2>{wr:.0f}%</h2></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="neon-gauge" style="border-color:#f2cc60"><p>TOP ROLE</p><h2>{top_lane}</h2></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="neon-gauge" style="border-color:#58a6ff"><p>AVG KDA</p><h2>{avg_kda:.2f}</h2></div>', unsafe_allow_html=True)

                # 2. المربعات السفلية (الرانك والمستري)
                st.write("---")
                b1, b2 = st.columns(2)
                with b1:
                    r_html = "<b>🏆 PLAYER RANK</b><br>"
                    if ranks:
                        for r in ranks: r_html += f"• {r.get('tier')} {r.get('rank')} ({r.get('leaguePoints')} LP)<br>"
                    else: r_html += "• Unranked"
                    st.markdown(f'<div class="card-bot" style="border-color:#00d4ff">{r_html}</div>', unsafe_allow_html=True)
                
                with b2:
                    m_html = "<b>⭐ TOP MASTERY</b><br>"
                    for c in mastery:
                        c_name = CHAMPS_MAP.get(str(c.get('championId')), "Unknown")
                        m_html += f"• {c_name}: Lvl {c.get('championLevel')}<br>"
                    st.markdown(f'<div class="card-bot" style="border-color:#f2cc60">{m_html}</div>', unsafe_allow_html=True)

                # 3. جدول الماتشات والتقارير
                st.write("---")
                st.subheader("Match History Reports")
                for m in match_list:
                    res_color = "#3fb950" if m['win'] else "#da3633"
                    with st.expander(f"🎮 {m['champ']} - {m['kda']} ({'WIN' if m['win'] else 'LOSS'})"):
                        col_img, col_txt = st.columns([1, 4])
                        with col_img:
                            st.image(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/champion/{m['champ']}.png", width=80)
                        with col_txt:
                            def get_c(r): return "#3fb950" if r == "GODLIKE" else "#58a6ff" if r == "GREAT" else "#f2cc60" if r == "DECENT" else "#da3633"
                            st.markdown(f"""
                                <h2 style="color:{res_color}">{"WIN" if m['win'] else "LOSS"}</h2>
                                💰 Gold: {m['gold']:,} <span style="color:{get_c(m['g_rate'])}">[{m['g_rate']}]</span><br>
                                🎯 Farm: {m['cs']} ({m['cs_m']} CS/m) <span style="color:{get_c(m['f_rate'])}">[{m['f_rate']}]</span><br>
                                👁️ Vision: {m['vision']} <span style="color:{get_c(m['v_rate'])}">[{m['v_rate']}]</span><br>
                                ⏱️ Duration: {m['time']} min
                            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"System Error: {e}")

st.caption("© 2026 | Developed by MAHMOUD ABDALLA")
