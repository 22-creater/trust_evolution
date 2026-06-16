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
# END AUTO-INJECTED Korean font setup


st.set_page_config(page_title="🤖 신뢰의 진화", page_icon="🤖", layout="wide")

st.markdown("""
<style>
  .stApp { 
    background: linear-gradient(135deg, #F7F7F5 0%, #E8E8E6 100%); 
  }
  .block-container { 
    padding-top: 1.5rem !important; 
  }
  hr { 
    border-color: #E0DED8; 
    margin: 1.5rem 0; 
  }

  /* 메트릭 카드 */
  div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
    border: 1px solid #E0DED8;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  div[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
    transition: all 0.3s ease;
  }

  /* 카드 컨테이너 */
  .card-container {
    background: white;
    border: 1.5px solid #E0DED8;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }

  /* 전략 태그 */
  .strategy-tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px;
    background: linear-gradient(135deg, #2E86AB 0%, #1D5B7A 100%);
    color: white;
    box-shadow: 0 2px 6px rgba(46,134,171,0.3);
  }

  /* 프로그레스 바 래퍼 */
  .progress-wrapper {
    background: white;
    border: 1.5px solid #E0DED8;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }

  /* 버튼 스타일 */
  .stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }
  .stButton > button:hover {
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
  }

  /* 실험 목록 카드 */
  .experiment-card {
    background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
    border: 1px solid #E0DED8;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  .experiment-card:hover {
    border-color: #2E86AB;
    box-shadow: 0 4px 12px rgba(46,134,171,0.2);
    transform: translateY(-2px);
  }

  /* 헤더 스타일 */
  h1, h2, h3 {
    color: #2C2C2A;
    font-weight: 700;
  }

  /* 탭 스타일 */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 12px 24px;
    font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ────────────────────────────────────────────────
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "progress_data" not in st.session_state:
    st.session_state.progress_data = {"generation": 0, "total": 0, "ai_score": 0, "social_score": 0}

init_db()

# ── 헤더 ──────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("# 🤖 신뢰의 진화 - AI 학습 시뮬레이션")
    st.caption("게임 이론 기반 강화학습 에이전트의 전략 진화 시뮬레이터")
with col2:
    now = datetime.now()
    st.markdown(
        f"<div style='text-align:right;padding-top:12px;'>"
        f"<span style='font-size:20px;font-weight:700;color:#2E86AB;'>🕐 {now.strftime('%H:%M:%S')}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

st.divider()

# ── 메인 탭 ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚀 새 시뮬레이션", "📊 결과 분석", "💾 실험 기록"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: 새 시뮬레이션
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("### 🌍 시뮬레이션 설정")

        # 나라별 프리셋
        preset_name = st.selectbox(
            "📍 나라별 MBTI 프리셋",
            options=list(COUNTRY_PRESETS.keys()),
            help="각 국가의 MBTI 성향 분포를 기반으로 한 전략 구성"
        )

        st.markdown("---")

        # 전략별 인구 조정
        st.markdown("#### 🏙️ 사회 구성원 설정")
        society = {}
        preset_values = COUNTRY_PRESETS[preset_name]

        for strategy_name in STRATEGY_MAP.keys():
            strategy = STRATEGY_MAP[strategy_name]()
            default_value = preset_values.get(strategy_name, 10)

            count = st.number_input(
                f"{strategy.emoji} {strategy_name}",
                min_value=0,
                max_value=100,
                value=default_value,
                step=1,
                help=strategy.description
            )
            if count > 0:
                society[strategy_name] = count

        total_population = sum(society.values())
        st.info(f"**총 인구:** {total_population}명")

        st.markdown("---")

        # 환경 설정
        st.markdown("#### ⚙️ 환경 설정")
        num_rounds = st.slider("매치당 라운드", 10, 500, 100, 10)
        num_generations = st.slider("학습 세대", 10, 1000, 200, 10)

        st.markdown("---")

        # 실행 버튼
        if st.session_state.simulation_running:
            if st.button("⏹ 시뮬레이션 중지", type="secondary", use_container_width=True):
                st.session_state.simulation_running = False
                st.rerun()
        else:
            if st.button("🚀 시뮬레이션 시작", type="primary", use_container_width=True):
                if total_population == 0:
                    st.error("최소 1명 이상의 NPC가 필요합니다!")
                else:
                    st.session_state.simulation_running = True
                    st.session_state.current_results = None
                    st.session_state.progress_data = {"generation": 0, "total": num_generations, "ai_score": 0, "social_score": 0}
                    st.rerun()

    with col_right:
        st.markdown("### 📈 실시간 모니터링")

        # 진행 상황
        if st.session_state.simulation_running:
            progress_data = st.session_state.progress_data

            # 프로그레스 바
            progress_pct = progress_data["generation"] / progress_data["total"] * 100 if progress_data["total"] > 0 else 0
            st.progress(progress_pct / 100)

            # 메트릭
            m1, m2, m3 = st.columns(3)
            m1.metric("진행 세대", f"{progress_data['generation']} / {progress_data['total']}")
            m2.metric("AI 점수", f"{progress_data['ai_score']:.2f}")
            m3.metric("사회 평균", f"{progress_data['social_score']:.2f}")

            # 시뮬레이션 실행
            def progress_callback(gen, total, ai_score, social_score):
                st.session_state.progress_data = {
                    "generation": gen,
                    "total": total,
                    "ai_score": ai_score,
                    "social_score": social_score
                }

            with st.spinner("🤖 AI가 학습 중입니다..."):
                results = run_simulation(society, num_rounds, num_generations, progress_callback)
                st.session_state.current_results = results
                st.session_state.simulation_running = False
                st.success("✅ 시뮬레이션 완료!")
                st.rerun()

        elif st.session_state.current_results:
            results = st.session_state.current_results

            st.success("✅ 시뮬레이션 완료!")

            # 요약 메트릭
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("최종 AI 점수", f"{results['generation_scores'][-1]:.2f}")
            m2.metric("사회 평균", f"{results['social_scores'][-1]:.2f}")
            score_change = results['generation_scores'][-1] - results['generation_scores'][0]
            m3.metric("점수 변화", f"{score_change:+.2f}")
            m4.metric("총 세대", results['num_generations'])

            # 저장 버튼
            if st.button("💾 실험 결과 저장", use_container_width=True):
                if save_experiment(preset_name, results):
                    st.success("저장 완료!")
                    time.sleep(1)
                    st.rerun()

        else:
            st.info("왼쪽에서 설정을 완료하고 '시뮬레이션 시작' 버튼을 클릭하세요.")

            # 프리셋 미리보기
            st.markdown("#### 📊 현재 프리셋 구성")
            preset_data = COUNTRY_PRESETS[preset_name]

            for strategy_name, count in preset_data.items():
                strategy = STRATEGY_MAP[strategy_name]()
                percentage = count / sum(preset_data.values()) * 100
                st.markdown(
                    f"<div style='margin:8px 0;'>"
                    f"<span style='font-size:18px;'>{strategy.emoji}</span> "
                    f"<strong>{strategy_name}</strong>: {count}명 ({percentage:.1f}%)"
                    f"</div>",
                    unsafe_allow_html=True
                )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: 결과 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    if st.session_state.current_results:
        results = st.session_state.current_results

        st.markdown("### 📊 시뮬레이션 결과 분석")

        # 기본 정보
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 세대", results['num_generations'])
        col2.metric("매치당 라운드", results['num_rounds'])
        col3.metric("총 인구", sum(results['society'].values()))
        score_change = results['generation_scores'][-1] - results['generation_scores'][0]
        col4.metric("AI 점수 변화", f"{score_change:+.2f}")

        st.divider()

        # 차트 영역
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📈 점수 추이", "🧠 행동 패턴", "🏙️ 사회 구성"])

        with chart_tab1:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

            # AI vs 사회 점수
            generations = range(1, len(results['generation_scores']) + 1)
            ax1.plot(list(generations), results['generation_scores'], 
                    linewidth=2.5, color='#2E86AB', label='AI 개인 점수', marker='o', markersize=3, markevery=len(list(generations))//20)
            ax1.plot(list(generations), results['social_scores'], 
                    linewidth=2.5, color='#E8952A', linestyle='--', label='사회 평균 점수', marker='s', markersize=3, markevery=len(list(generations))//20)
            ax1.fill_between(list(generations), results['generation_scores'], results['social_scores'], 
                            alpha=0.15, color='#2E86AB')
            ax1.set_xlabel('세대', fontsize=11, fontweight='bold')
            ax1.set_ylabel('평균 점수', fontsize=11, fontweight='bold')
            ax1.set_title('📊 AI 개인 점수 vs 사회 평균 점수', fontsize=12, fontweight='bold')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)

            # 전략별 성과
            strategy_names = list(results['strategy_scores'].keys())
            final_scores = [results['strategy_scores'][name][-1] for name in strategy_names]
            colors = plt.cm.Set3(range(len(strategy_names)))
            bars = ax2.barh(strategy_names, final_scores, color=colors, height=0.7)
            ax2.set_xlabel('최종 AI 점수', fontsize=11, fontweight='bold')
            ax2.set_title('📊 전략별 AI 성과', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='x', linestyle=':', linewidth=0.8)
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                        f'{width:.1f}', ha='left', va='center', fontsize=9, fontweight='bold')

            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with chart_tab2:
            fig, ax = plt.subplots(figsize=(12, 8))

            matrix = results['final_similarity']
            ref_names = list(matrix.keys())
            opp_names = list(next(iter(matrix.values())).keys())
            heat_data = np.array([[matrix[r][o] for o in opp_names] for r in ref_names])

            im = ax.imshow(heat_data, cmap='YlGnBu', aspect='auto', vmin=0, vmax=100)
            ax.set_xticks(range(len(opp_names)))
            ax.set_yticks(range(len(ref_names)))
            ax.set_xticklabels(opp_names, rotation=30, ha='right', fontsize=10)
            ax.set_yticklabels(ref_names, fontsize=10)
            ax.set_title('🧠 AI 행동 패턴 매트릭스 (상대별 전략 유사도 %)', fontsize=13, fontweight='bold', pad=20)
            ax.set_xlabel('상대 전략', fontsize=11, fontweight='bold')
            ax.set_ylabel('레퍼런스 전략', fontsize=11, fontweight='bold')

            for i in range(len(ref_names)):
                for j in range(len(opp_names)):
                    val = heat_data[i, j]
                    color = 'white' if val > 60 else 'black'
                    ax.text(j, i, f'{val:.0f}%', ha='center', va='center', 
                           fontsize=9, fontweight='bold', color=color)

            plt.colorbar(im, ax=ax, shrink=0.8, label='유사도 (%)')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # 분석 결과 텍스트
            st.markdown("#### 💡 행동 패턴 분석")

            dominant_counts = {}
            for opp_name in opp_names:
                best_ref = max(ref_names, key=lambda r: matrix[r][opp_name])
                dominant_counts[best_ref] = dominant_counts.get(best_ref, 0) + 1

            overall_dominant = max(dominant_counts, key=dominant_counts.get)
            dominant_strategy = STRATEGY_MAP[overall_dominant]()

            st.info(
                f"**AI는 전반적으로 '{overall_dominant}' {dominant_strategy.emoji} 패턴에 가장 많이 수렴했습니다.**\n\n"
                f"상대에 따라 전략을 동적으로 조정하며, 강화학습을 통해 최적의 행동을 찾아갔습니다."
            )

        with chart_tab3:
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots(figsize=(7, 7))
                society = results['society']
                labels = [f"{STRATEGY_MAP[n]().emoji} {n}\n({c}명)" for n, c in society.items()]
                colors = plt.cm.Pastel1(range(len(society)))
                ax.pie(list(society.values()), labels=labels, colors=colors, 
                      autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
                ax.set_title('🏙️ 사회 구성 분포', fontsize=13, fontweight='bold', pad=20)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

            with col2:
                st.markdown("#### 📋 구성원 상세")
                total = sum(society.values())
                for strategy_name, count in society.items():
                    strategy = STRATEGY_MAP[strategy_name]()
                    percentage = count / total * 100
                    st.markdown(
                        f"<div style='background:white; border:1px solid #E0DED8; border-radius:8px; "
                        f"padding:12px; margin:8px 0;'>"
                        f"<span style='font-size:24px;'>{strategy.emoji}</span> "
                        f"<strong style='font-size:15px;'>{strategy_name}</strong><br>"
                        f"<span style='color:#666; font-size:13px;'>{count}명 ({percentage:.1f}%)</span><br>"
                        f"<span style='color:#888; font-size:12px;'>{strategy.description}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
    else:
        st.info("아직 시뮬레이션 결과가 없습니다. '새 시뮬레이션' 탭에서 실행해주세요.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3: 실험 기록
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.markdown("### 💾 저장된 실험 기록")

    experiments = load_experiments()

    if experiments:
        for exp in experiments:
            with st.expander(
                f"🧪 {exp['preset_name']} | 세대: {exp['num_generations']} | "
                f"AI 점수: {exp['final_ai_score']:.2f} | "
                f"{exp['created_at'][:16]}"
            ):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown(f"**프리셋:** {exp['preset_name']}")
                    st.markdown(f"**라운드:** {exp['num_rounds']}")
                    st.markdown(f"**세대:** {exp['num_generations']}")

                with col2:
                    st.markdown(f"**최종 AI 점수:** {exp['final_ai_score']:.2f}")
                    st.markdown(f"**최종 사회 점수:** {exp['final_social_score']:.2f}")
                    st.markdown(f"**생성 시각:** {exp['created_at'][:19]}")

                with col3:
                    if st.button("📂 상세보기", key=f"load_{exp['id']}"):
                        detail = load_experiment_detail(exp['id'])
                        if detail:
                            st.session_state.current_results = detail
                            st.success("불러오기 완료!")
                            time.sleep(1)
                            st.rerun()

                    if st.button("🗑 삭제", key=f"del_{exp['id']}"):
                        if delete_experiment(exp['id']):
                            st.success("삭제 완료!")
                            time.sleep(1)
                            st.rerun()
    else:
        st.info("아직 저장된 실험이 없습니다. 시뮬레이션 완료 후 저장해주세요.")

# ── 자동 새로고침 (시뮬레이션 실행 중에만) ────────────────────
if st.session_state.simulation_running:
    time.sleep(0.5)
    st.rerun()
