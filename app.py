import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from datetime import datetime
import time
from simulation import STRATEGY_MAP, COUNTRY_PRESETS, run_simulation
from db import init_db, save_experiment, load_experiments, load_experiment_detail, delete_experiment

# AUTO-INJECTED: Korean font setup for matplotlib
import os as _os
import matplotlib.font_manager as _fm
import matplotlib.pyplot as _plt
if not any('NanumGothic' in f.name for f in _fm.fontManager.ttflist):
    for _font in ['/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                  '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf']:
        if _os.path.exists(_font):
            _fm.fontManager.addfont(_font)
_plt.rcParams.update({'font.family': 'NanumGothic', 'axes.unicode_minus': False})
del _os, _fm, _plt

st.set_page_config(page_title="🤖 신뢰의 진화", page_icon="🤖", layout="wide")

st.markdown("""
<style>
  .stApp { background: linear-gradient(135deg, #F7F7F5 0%, #E8E8E6 100%); }
  div[data-testid="metric-container"] { background: white; border: 1px solid #E0DED8; border-radius: 12px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ────────────────────────────────────────────────
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "current_results" not in st.session_state:
    st.session_state.current_results = None

init_db()

# ── 헤더 ──────────────────────────────────────────────────────
st.markdown("# 🤖 신뢰의 진화 - AI 학습 시뮬레이션")
st.divider()

# ── 메인 탭 ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚀 새 시뮬레이션", "📊 결과 분석", "💾 실험 기록"])

with tab1:
    col_left, col_right = st.columns([2, 3])
    with col_left:
        preset_name = st.selectbox("📍 나라별 MBTI 프리셋", options=list(COUNTRY_PRESETS.keys()))
        society = {}
        preset_values = COUNTRY_PRESETS[preset_name]
        for strategy_name in STRATEGY_MAP.keys():
            count = st.number_input(f"{strategy_name}", min_value=0, max_value=100, value=preset_values.get(strategy_name, 10))
            if count > 0: society[strategy_name] = count
        
        num_rounds = st.slider("매치당 라운드", 10, 500, 100)
        num_generations = st.slider("학습 세대", 10, 1000, 200)

        if st.button("🚀 시뮬레이션 시작", type="primary"):
            st.session_state.simulation_running = True
            st.session_state.current_results = None

    with col_right:
        if st.session_state.simulation_running:
            with st.status("🤖 AI가 학습 중입니다...", expanded=True) as status:
                results = run_simulation(society, num_rounds, num_generations)
                st.session_state.current_results = results
                st.session_state.simulation_running = False
                status.update(label="✅ 시뮬레이션 완료!", state="complete")
            st.rerun() # 완료 직후 한 번만 리런
        
        elif st.session_state.current_results:
            st.success("✅ 시뮬레이션 완료! '결과 분석' 탭을 확인하세요.")
            if st.button("💾 실험 결과 저장"):
                if save_experiment(preset_name, st.session_state.current_results):
                    st.success("저장 완료!")

# ━━━━━━━━ TAB 2, TAB 3 코드는 기존과 동일하게 유지 ━━━━━━━━
with tab2:
    if st.session_state.current_results:
        results = st.session_state.current_results
        st.markdown("### 📊 시뮬레이션 결과")
        # (기존 차트 시각화 코드...)
    else:
        st.info("시뮬레이션 결과가 없습니다.")

with tab3:
    # (기존 실험 기록 코드...)
    pass
