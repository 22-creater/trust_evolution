import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import time
from simulation import STRATEGY_MAP, COUNTRY_PRESETS, run_simulation
from db import init_db, save_experiment

st.set_page_config(page_title="🤖 신뢰의 진화", page_icon="🤖", layout="wide")

# 세션 초기화
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "current_results" not in st.session_state:
    st.session_state.current_results = None

init_db()

st.markdown("# 🤖 신뢰의 진화 - AI 학습 시뮬레이션")
st.divider()

tab1, tab2, tab3 = st.tabs(["🚀 새 시뮬레이션", "📊 결과 분석", "💾 실험 기록"])

with tab1:
    col_left, col_right = st.columns([1, 2])
    with col_left:
        preset_name = st.selectbox("📍 나라별 MBTI 프리셋", options=list(COUNTRY_PRESETS.keys()))
        society = {name: st.number_input(f"{name}", 0, 100, COUNTRY_PRESETS[preset_name].get(name, 10)) 
                   for name in STRATEGY_MAP.keys()}
        num_rounds = st.slider("매치당 라운드", 10, 500, 100)
        num_generations = st.slider("학습 세대", 10, 1000, 200)

        # 시뮬레이션 실행 버튼
        if st.button("🚀 시뮬레이션 시작", type="primary"):
            st.session_state.simulation_running = True
            st.session_state.current_results = None
            st.rerun()

    with col_right:
        if st.session_state.simulation_running:
            # 시뮬레이션 진행 중
            with st.spinner("🤖 AI가 방대한 연산을 수행 중입니다. 잠시만 기다려주세요..."):
                # callback을 아예 제거하여 UI 업데이트 충돌 원천 차단
                results = run_simulation(society, num_rounds, num_generations, progress_callback=None)
                st.session_state.current_results = results
                st.session_state.simulation_running = False
            st.rerun() # 계산 완료 후 딱 한 번만 전체 갱신
        
        elif st.session_state.current_results:
            st.success("✅ 시뮬레이션 완료! 결과 탭에서 확인하세요.")
            if st.button("💾 실험 결과 저장"):
                if save_experiment(preset_name, st.session_state.current_results):
                    st.success("저장 성공!")
        else:
            st.info("좌측에서 설정을 마치고 시뮬레이션을 시작하세요.")

# (TAB 2, TAB 3 코드는 기존과 동일하게 유지)
