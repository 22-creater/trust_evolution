import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

from simulation import STRATEGY_MAP, COUNTRY_PRESETS, analyze_ai_behavior
from simulation import AdaptiveAI, play_match

# ── 한글 폰트 설정 ──────────────────────────────────────────────────
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

_korean_font = None
for _f in _FONT_CANDIDATES:
    if os.path.exists(_f):
        fm.fontManager.addfont(_f)
        _prop = fm.FontProperties(fname=_f)
        _korean_font = _prop.get_name()
        break

def apply_korean_font(ax):
    """차트 객체에 한글 폰트를 일괄 적용하는 함수"""
    if _korean_font:
        font_prop = {"family": _korean_font}
        ax.set_title(ax.get_title(), **font_prop)
        ax.set_xlabel(ax.get_xlabel(), **font_prop)
        ax.set_ylabel(ax.get_ylabel(), **font_prop)
        if ax.get_legend():
            plt.setp(ax.get_legend().get_texts(), **font_prop)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(fm.FontProperties(family=_korean_font))

if _korean_font:
    fm._load_fontmanager(try_read_cache=False)
    matplotlib.rcParams["font.family"] = [_korean_font]
    matplotlib.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.family"] = [_korean_font]
    plt.rcParams["axes.unicode_minus"] = False
else:
    matplotlib.rcParams["axes.unicode_minus"] = False
    plt.rcParams["axes.unicode_minus"] = False

# ── KST 헬퍼 ──────────────────────────────────────────────────────
KST = ZoneInfo("Asia/Seoul")

def now_kst() -> datetime:
    return datetime.now(KST)

# ── 페이지 설정 ───────────────────────────────────────────────────
st.set_page_config(page_title="신뢰의 진화", page_icon="🤖", layout="wide")

st.markdown("""
<style>
  .stApp { background: linear-gradient(135deg, #F7F7F5 0%, #ECEAE6 100%); }
  .block-container { padding-top: 1.5rem !important; }
  div[data-testid="metric-container"] {
    background: white; border: 1px solid #E0DED8; border-radius: 12px;
    padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  .stButton > button { border-radius: 10px; font-weight: 600; }
  h1, h2, h3 { color: #2C2C2A; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ───────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state["results"] = None

# ── 헤더 ─────────────────────────────────────────────────────────
c1, c2 = st.columns([5, 1])
with c1:
    st.markdown("# 🤖 신뢰의 진화 — AI 학습 시뮬레이션")
    st.caption("게임 이론 기반 강화학습 에이전트의 전략 진화 시뮬레이터")
with c2:
    st.markdown(
        f"<div style='text-align:right;padding-top:14px;'>"
        f"<span style='font-size:18px;font-weight:700;color:#2E86AB;'>"
        f"🕐 {now_kst().strftime('%H:%M:%S')} KST</span></div>",
        unsafe_allow_html=True,
    )
st.divider()

tab1, tab2 = st.tabs(["🚀 새 시뮬레이션", "📊 결과 분석"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("### 🌍 시뮬레이션 설정")
        preset_name = st.selectbox("📍 나라별 MBTI 프리셋", list(COUNTRY_PRESETS.keys()))
        preset_values = COUNTRY_PRESETS[preset_name]
        if "selected_preset" not in st.session_state:
            st.session_state.selected_preset = preset_name

        if st.session_state.selected_preset != preset_name:
            for sname in STRATEGY_MAP:
                st.session_state[f"pop_{sname}"] = preset_values.get(sname, 0)
            st.session_state.selected_preset = preset_name
            st.rerun()
        st.markdown("---")
        st.markdown("#### 🏙️ 사회 구성원 설정")

        society = {}
        for sname in STRATEGY_MAP:
            if f"pop_{sname}" not in st.session_state:
                st.session_state[f"pop_{sname}"] = preset_values.get(sname, 0)
              
        for sname, Cls in STRATEGY_MAP.items():
            s = Cls()
            cnt = st.number_input(
                f"{s.emoji} {sname}", min_value=0, max_value=100,
                step=1, help=s.description, key=f"pop_{sname}",
            )
            if cnt > 0:
                society[sname] = cnt

        total_pop = sum(society.values())
        st.info(f"**총 인구:** {total_pop}명")
        st.markdown("---")
        st.markdown("#### ⚙️ 환경 설정")
        num_rounds = st.slider("매치당 라운드", 10, 500, 100, 10)
        num_generations = st.slider("학습 세대", 10, 500, 200, 10)
        st.markdown("---")
        run_btn = st.button("🚀 시뮬레이션 시작", type="primary",
                            use_container_width=True, disabled=(total_pop == 0))

    with col_right:
        st.markdown("### 📈 실시간 모니터링")

        if run_btn:
            prog_bar = st.progress(0)
            stat_cols = st.columns(3)
            gen_ph = stat_cols[0].empty()
            ai_ph  = stat_cols[1].empty()
            soc_ph = stat_cols[2].empty()
            msg_ph = st.empty()
            msg_ph.info("🤖 AI가 학습 중입니다...")

            population = [STRATEGY_MAP[n]() for n, c in society.items() for _ in range(c)]
            ai = AdaptiveAI()
            gen_scores, soc_scores = [], []
            strat_scores = defaultdict(list)
            eps_hist, sim_evo = [], []
            snap = {0, num_generations//4, num_generations//2, 3*num_generations//4, num_generations-1}

            for gen in range(num_generations):
                t_ai = t_npc = 0
                gs = defaultdict(lambda: {"ai": 0, "cnt": 0})
                for npc in population:
                    a, n = play_match(ai, npc, num_rounds)
                    t_ai += a; t_npc += n
                    gs[npc.name]["ai"] += a
                    gs[npc.name]["cnt"] += 1

                avg_ai  = t_ai / len(population)
                avg_soc = (t_ai + t_npc) / (len(population) * 2)
                gen_scores.append(round(avg_ai, 4))
                soc_scores.append(round(avg_soc, 4))
                eps_hist.append(round(ai.epsilon, 4))
                for nm, s in gs.items():
                    strat_scores[nm].append(round(s["ai"] / s["cnt"], 4))

                if gen in snap:
                    sim_evo.append((gen, analyze_ai_behavior(ai)))
                ai.decay_epsilon()

                if gen % max(1, num_generations // 50) == 0 or gen == num_generations - 1:
                    pct = (gen + 1) / num_generations
                    prog_bar.progress(pct)
                    gen_ph.metric("진행 세대", f"{gen+1}/{num_generations}")
                    ai_ph.metric("AI 점수", f"{avg_ai:.2f}")
                    soc_ph.metric("사회 평균", f"{avg_soc:.2f}")

            final_sim = analyze_ai_behavior(ai)
            results = {
                "generation_scores": gen_scores, "social_scores": soc_scores,
                "strategy_scores": dict(strat_scores), "epsilon_history": eps_hist,
                "similarity_evolution": sim_evo, "final_similarity": final_sim,
                "society": society, "num_rounds": num_rounds,
                "num_generations": num_generations, "preset_name": preset_name,
                "timestamp": now_kst().isoformat(),
            }
            st.session_state.results = results
            msg_ph.success("✅ 완료! '결과 분석' 탭에서 확인하세요.")
            st.rerun()

        elif st.session_state.results:
            r = st.session_state.results
            st.success("✅ 이전 결과가 있습니다. '결과 분석' 탭을 확인하세요.")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("최종 AI 점수",  f"{r['generation_scores'][-1]:.2f}")
            m2.metric("최종 사회 평균", f"{r['social_scores'][-1]:.2f}")
            m3.metric("점수 변화",     f"{r['generation_scores'][-1]-r['generation_scores'][0]:+.2f}")
            m4.metric("총 세대",       r["num_generations"])

        else:
            st.info("왼쪽에서 설정 후 시뮬레이션 시작 버튼을 클릭하세요.")
            st.markdown("#### 📊 현재 구성원 설정")
            current_total = sum(society.values()) if society else 1
            for sname, cnt in society.items():
                s = STRATEGY_MAP[sname]()
                pct = cnt / current_total * 100
                st.markdown(f"<div style='margin:6px 0;'><span style='font-size:18px;'>{s.emoji}</span> <strong>{sname}</strong>: {cnt}명 ({pct:.1f}%)</div>", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    r = st.session_state.results
    if not r:
        st.info("아직 결과가 없습니다. '새 시뮬레이션' 탭에서 실행해주세요.")
    else:
        st.markdown("### 📊 시뮬레이션 결과 분석")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 세대",       r["num_generations"])
        c2.metric("매치당 라운드", r["num_rounds"])
        c3.metric("총 인구",       sum(r["society"].values()))
        c4.metric("AI 점수 변화",  f"{r['generation_scores'][-1]-r['generation_scores'][0]:+.2f}")
        st.divider()

        ct1, ct2, ct3, ct4 = st.tabs(["📈 점수 추이", "🧠 행동 패턴", "🏙️ 사회 구성", "📉 학습률"])

        with ct1:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            gens = list(range(1, len(r["generation_scores"]) + 1))
            ax1.plot(gens, r["generation_scores"], lw=2.5, color="#2E86AB", label="AI 개인 점수")
            ax1.plot(gens, r["social_scores"], lw=2.5, color="#E8952A", linestyle="--", label="사회 평균 점수")
            ax1.fill_between(gens, r["generation_scores"], r["social_scores"], where=[a > s for a, s in zip(r["generation_scores"], r["social_scores"])], alpha=0.15, color="#2E86AB")
            ax1.fill_between(gens, r["generation_scores"], r["social_scores"], where=[a <= s for a, s in zip(r["generation_scores"], r["social_scores"])], alpha=0.15, color="#E8952A")
            ax1.set(xlabel="세대", ylabel="평균 점수", title="AI 점수 vs 사회 평균")
            apply_korean_font(ax1)
            ax1.legend(); ax1.grid(True, alpha=0.3)

            snames = list(r["strategy_scores"].keys())
            fscores = [r["strategy_scores"][n][-1] for n in snames]
            bars = ax2.barh(snames, fscores, color=plt.cm.Set3(range(len(snames))), height=0.7)
            for b in bars:
                ax2.text(b.get_width()+0.5, b.get_y()+b.get_height()/2, f"{b.get_width():.1f}", va="center", fontsize=9, fontweight="bold")
            ax2.set(xlabel="최종 AI 점수", title="전략별 AI 성과")
            apply_korean_font(ax2)
            ax2.grid(True, alpha=0.3, axis="x")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with ct2:
            fig, ax = plt.subplots(figsize=(11, 7))
            matrix = r["final_similarity"]
            rnames = list(matrix.keys())
            onames = list(next(iter(matrix.values())).keys())
            heat = np.array([[matrix[rf][op] for op in onames] for rf in rnames])
            im = ax.imshow(heat, cmap="YlGnBu", aspect="auto", vmin=0, vmax=100)
            ax.set_xticks(range(len(onames))); ax.set_yticks(range(len(rnames)))
            ax.set_xticklabels(onames, rotation=30, ha="right", fontsize=10)
            ax.set_yticklabels(rnames, fontsize=10)
            ax.set_title("AI 행동 패턴 매트릭스 (상대별 전략 유사도 %)", fontsize=13, fontweight="bold", pad=16)
            apply_korean_font(ax)
            ax.set_xlabel("상대 전략", fontsize=11); ax.set_ylabel("레퍼런스 전략", fontsize=11)
            for i in range(len(rnames)):
                for j in range(len(onames)):
                    v = heat[i, j]
                    ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9, fontweight="bold", color="white" if v > 60 else "black")
            plt.colorbar(im, ax=ax, shrink=0.8, label="유사도 (%)")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with ct3:
            cc1, cc2 = st.columns(2)
            with cc1:
                fig, ax = plt.subplots(figsize=(7, 7))
                soc = r["society"]
                labels = [f"{STRATEGY_MAP[n]().emoji} {n}\n({c}명)" for n, c in soc.items()]
                ax.pie(list(soc.values()), labels=labels, colors=plt.cm.Pastel1(range(len(soc))), autopct="%1.1f%%", startangle=90, textprops={"fontsize": 10, "fontweight": "bold"})
                ax.set_title("사회 구성 분포", fontsize=13, fontweight="bold", pad=16)
                apply_korean_font(ax)
                plt.tight_layout(); st.pyplot(fig); plt.close()
            with cc2:
                st.markdown("#### 📋 구성원 상세")
                total = sum(soc.values())
                for sname, cnt in soc.items():
                    s = STRATEGY_MAP[sname]()
                    pct = cnt / total * 100
                    st.markdown(f"<div style='background:white;border:1px solid #E0DED8;border-radius:8px;padding:12px;margin:8px 0;'><span style='font-size:22px;'>{s.emoji}</span> <strong>{sname}</strong><br><span style='color:#666;font-size:13px;'>{cnt}명 ({pct:.1f}%)</span></div>", unsafe_allow_html=True)

        with ct4:
            if r.get("epsilon_history"):
                fig, ax = plt.subplots(figsize=(12, 4))
                gens = list(range(1, len(r["epsilon_history"]) + 1))
                ax.plot(gens, r["epsilon_history"], lw=2.5, color="#9B59B6", label="탐색률 (epsilon)")
                ax.set(xlabel="세대", ylabel="Epsilon", title="탐색률 감소 과정 (탐색 → 활용)")
                apply_korean_font(ax)
                ax.legend(); ax.grid(True, alpha=0.3)
                plt.tight_layout(); st.pyplot(fig); plt.close()
