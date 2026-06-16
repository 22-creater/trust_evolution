"""
app.py - 신뢰의 진화 Streamlit 앱 (Simpleton 제거, 비율 업데이트 버전)
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import datetime
from collections import defaultdict

from simulation import STRATEGY_MAP, COUNTRY_PRESETS, analyze_ai_behavior
from simulation import AdaptiveAI, play_match

# 한글 폰트 설정
for _f in ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
           "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]:
    if os.path.exists(_f):
        fm.fontManager.addfont(_f)
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False})

st.set_page_config(page_title="신뢰의 진화", page_icon="🤖", layout="wide")

# CSS 스타일
st.markdown("""
<style>
  .stApp { background: linear-gradient(135deg, #F7F7F5 0%, #ECEAE6 100%); }
  div[data-testid="metric-container"] { background: white; border: 1px solid #E0DED8; border-radius: 12px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# 세션 초기화
if "results" not in st.session_state:
    st.session_state.results = None

st.markdown("# 🤖 신뢰의 진화 — AI 학습 시뮬레이션")
st.divider()

tab1, tab2 = st.tabs(["🚀 새 시뮬레이션", "📊 결과 분석"])

with tab1:
    col_left, col_right = st.columns([1, 2])
    with col_left:
        preset_name = st.selectbox("📍 나라별 MBTI 프리셋", list(COUNTRY_PRESETS.keys()))
        preset_values = COUNTRY_PRESETS[preset_name]
        
        society = {}
        st.markdown("#### 🏙️ 사회 구성원 설정")
        for sname, Cls in STRATEGY_MAP.items():
            s = Cls()
            cnt = st.number_input(f"{s.emoji} {sname}", 0, 100, preset_values.get(sname, 20))
            if cnt > 0: society[sname] = cnt
        
        num_rounds = st.slider("매치당 라운드", 10, 500, 100)
        num_generations = st.slider("학습 세대", 10, 500, 200)
        run_btn = st.button("🚀 시뮬레이션 시작", type="primary")

    with col_right:
        if run_btn:
            prog_bar = st.progress(0)
            population = [STRATEGY_MAP[n]() for n, c in society.items() for _ in range(c)]
            ai = AdaptiveAI()
            gen_scores, soc_scores, strat_scores = [], [], defaultdict(list)
            
            for gen in range(num_generations):
                t_ai = t_npc = 0
                for npc in population:
                    a, n = play_match(ai, npc, num_rounds)
                    t_ai += a; t_npc += n
                
                gen_scores.append(t_ai / len(population))
                soc_scores.append((t_ai + t_npc) / (len(population) * 2))
                prog_bar.progress((gen + 1) / num_generations)
                ai.decay_epsilon()
            
            st.session_state.results = {
                "generation_scores": gen_scores, "social_scores": soc_scores,
                "society": society, "num_rounds": num_rounds, "num_generations": num_generations,
                "final_similarity": analyze_ai_behavior(ai)
            }
            st.success("✅ 시뮬레이션 완료!")

with tab2:
    if st.session_state.results:
        r = st.session_state.results
        st.line_chart({"AI 점수": r["generation_scores"], "사회 평균": r["social_scores"]})
    else:
        st.info("결과가 없습니다.")
