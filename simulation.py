"""
simulation.py - 게임 이론 엔진 + 전략 클래스
"""
import numpy as np
from collections import defaultdict
from datetime import datetime

# ─────────────────────────────────────────────
# 전략 클래스
# ─────────────────────────────────────────────

class Strategy:
    def __init__(self, name, description, emoji):
        self.name = name
        self.description = description
        self.emoji = emoji
        self.reset()

    def reset(self): pass
    def decide(self, opponent_history): raise NotImplementedError


class AlwaysCooperate(Strategy):
    def __init__(self):
        super().__init__("Always Cooperate", "무조건 협력. 착하지만 착취당하기 쉬워요.", "🤝")
    def decide(self, h): return True


class AlwaysCheat(Strategy):
    def __init__(self):
        super().__init__("Always Cheat", "무조건 배신. 단기 이득은 크지만 신뢰를 잃어요.", "😈")
    def decide(self, h): return False


class Copycat(Strategy):
    def __init__(self):
        super().__init__("Copycat", "눈에는 눈! 상대방의 이전 행동을 그대로 따라합니다.", "🐱")
    def decide(self, h): return h[-1] if h else True


class Grudger(Strategy):
    def __init__(self):
        super().__init__("Grudger", "한 번 배신당하면 영원히 복수합니다. 용서는 없어요!", "😠")
    def reset(self): self.betrayed = False
    def decide(self, h):
        if self.betrayed: return False
        if h and not h[-1]:
            self.betrayed = True
            return False
        return True


class Detective(Strategy):
    def __init__(self):
        super().__init__("Detective", "4턴 탐색 후 호구면 착취, 아니면 Copycat으로 전환.", "🕵️")
    def reset(self):
        self.turn = 0
        self.opponent_cheated = False
    def decide(self, h):
        self.turn += 1
        if self.turn <= 4:
            return [True, False, True, True][self.turn - 1]
        if self.turn == 5 and len(h) >= 4:
            self.opponent_cheated = not all(h[:4])
        if self.turn > 4:
            return (h[-1] if h else True) if self.opponent_cheated else False
        return True


# class Simpleton(Strategy):
#     def __init__(self):
#         super().__init__("Simpleton", "상대가 협력하면 같은 행동을, 배신하면 행동을 바꿉니다.", "😊")
#     def reset(self): self.last_move = True
#     def decide(self, h):
#         if not h: return True
#         self.last_move = self.last_move if h[-1] else not self.last_move
#         return self.last_move


class AdaptiveAI(Strategy):
    def __init__(self, lr=0.1, gamma=0.95,
                 eps_start=0.9, eps_end=0.05, eps_decay=0.97):
        super().__init__("Adaptive AI", "강화학습으로 최적 전략을 스스로 찾아갑니다.", "🤖")
        self.lr = lr
        self.gamma = gamma
        self.epsilon = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.q_table = defaultdict(lambda: [0.0, 0.0])
        self.reset()

    def decay_epsilon(self):
        self.epsilon = max(self.eps_end, self.epsilon * self.eps_decay)

    def reset(self):
        self.last_state = None
        self.last_action = None

    def _state(self, h):
        return "start" if not h else tuple(h[-3:])

    def decide(self, h):
        s = self._state(h)
        if np.random.random() < self.epsilon:
            action = bool(np.random.choice([True, False]))
        else:
            q = self.q_table[s]
            action = q[0] >= q[1]
        self.last_state = s
        self.last_action = action
        return action

    def update(self, reward, h):
        if self.last_state is None: return
        ns = self._state(h)
        idx = 0 if self.last_action else 1
        cq = self.q_table[self.last_state][idx]
        self.q_table[self.last_state][idx] = cq + self.lr * (
            reward + self.gamma * max(self.q_table[ns]) - cq
        )


# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────

STRATEGY_MAP = {
    "Always Cooperate": AlwaysCooperate,
    "Always Cheat":     AlwaysCheat,
    "Copycat":          Copycat,
    "Grudger":          Grudger,
    "Detective":        Detective,
    # "Simpleton":        Simpleton,
}

COUNTRY_PRESETS = {
    "한국 (MBTI 기반)": {"Always Cooperate": 33, "Always Cheat": 7,  "Copycat": 20, "Grudger": 13, "Detective": 27},
    "일본 (MBTI 기반)": {"Always Cooperate": 37, "Always Cheat": 6,  "Copycat": 17, "Grudger": 14, "Detective": 26},
    "중국 (MBTI 기반)": {"Always Cooperate": 26, "Always Cheat": 8,  "Copycat": 24, "Grudger": 13, "Detective": 29},
    "미국 (MBTI 기반)": {"Always Cooperate": 36, "Always Cheat": 3,  "Copycat": 21, "Grudger": 11, "Detective": 29},
    "균등 분포":        {"Always Cooperate": 10, "Always Cheat": 10, "Copycat": 10, "Grudger": 10,"Detective": 10},
}


# ─────────────────────────────────────────────
# 게임 엔진
# ─────────────────────────────────────────────

def play_match(ai, npc, rounds):
    ai.reset(); npc.reset()
    h_ai, h_npc = [], []
    s_ai = s_npc = 0
    for _ in range(rounds):
        m_ai  = ai.decide(h_npc.copy())
        m_npc = npc.decide(h_ai.copy())
        if   m_ai and m_npc:     r_ai, r_npc = 2, 2
        elif m_ai and not m_npc: r_ai, r_npc = 0, 3
        elif not m_ai and m_npc: r_ai, r_npc = 3, 0
        else:                    r_ai, r_npc = 1, 1
        h_ai.append(m_ai); h_npc.append(m_npc)
        s_ai += r_ai;      s_npc += r_npc
        ai.update(r_ai, h_npc)
    return s_ai, s_npc


def analyze_ai_behavior(ai, rounds=100):
    """AI 행동을 각 레퍼런스 전략과 비교 → 유사도 매트릭스 반환"""
    # AI 시퀀스 수집
    ai_seqs = {}
    for opp_name, OppClass in STRATEGY_MAP.items():
        opp = OppClass(); ai.reset(); opp.reset()
        h_ai, h_opp, seq = [], [], []
        for _ in range(rounds):
            m_ai = ai.decide(h_opp.copy())
            m_opp = opp.decide(h_ai.copy())
            r = 2 if (m_ai and m_opp) else 0 if m_ai else 3 if m_opp else 1
            h_ai.append(m_ai); h_opp.append(m_opp); seq.append(m_ai)
            ai.update(r, h_opp)
        ai_seqs[opp_name] = seq

    # 레퍼런스 시퀀스 수집
    ref_seqs = {}
    for ref_name, RefClass in STRATEGY_MAP.items():
        ref_seqs[ref_name] = {}
        for opp_name, OppClass in STRATEGY_MAP.items():
            ref = RefClass(); opp = OppClass()
            ref.reset(); opp.reset()
            h_r, h_o, seq = [], [], []
            for _ in range(rounds):
                m_r = ref.decide(h_o.copy())
                m_o = opp.decide(h_r.copy())
                h_r.append(m_r); h_o.append(m_o); seq.append(m_r)
            ref_seqs[ref_name][opp_name] = seq

    # 매트릭스 계산
    matrix = {}
    for ref in STRATEGY_MAP:
        matrix[ref] = {}
        for opp in STRATEGY_MAP:
            matches = sum(a == r for a, r in zip(ai_seqs[opp], ref_seqs[ref][opp]))
            matrix[ref][opp] = round(matches / rounds * 100, 1)
    return matrix


def run_simulation(society: dict, num_rounds: int, num_generations: int):
    """
    시뮬레이션 실행 — 결과 dict 반환
    진행상황은 반환값 내 generation_scores 길이로 파악
    """
    population = [STRATEGY_MAP[n]() for n, c in society.items() for _ in range(c)]
    ai = AdaptiveAI()

    generation_scores   = []
    social_scores       = []
    strategy_scores     = defaultdict(list)
    epsilon_history     = []
    similarity_evolution = []

    snap_points = {
        0,
        num_generations // 4,
        num_generations // 2,
        3 * num_generations // 4,
        num_generations - 1,
    }

    for gen in range(num_generations):
        total_ai = total_npc = 0
        gen_s = defaultdict(lambda: {"ai": 0, "cnt": 0})

        for npc in population:
            a, n = play_match(ai, npc, num_rounds)
            total_ai += a; total_npc += n
            gen_s[npc.name]["ai"]  += a
            gen_s[npc.name]["cnt"] += 1

        avg_ai     = total_ai / len(population)
        avg_social = (total_ai + total_npc) / (len(population) * 2)
        generation_scores.append(round(avg_ai, 4))
        social_scores.append(round(avg_social, 4))
        epsilon_history.append(round(ai.epsilon, 4))

        for name, s in gen_s.items():
            strategy_scores[name].append(round(s["ai"] / s["cnt"], 4))

        if gen in snap_points:
            similarity_evolution.append((gen, analyze_ai_behavior(ai)))

        ai.decay_epsilon()

    final_similarity = analyze_ai_behavior(ai)

    return {
        "generation_scores":    generation_scores,
        "social_scores":        social_scores,
        "strategy_scores":      dict(strategy_scores),
        "epsilon_history":      epsilon_history,
        "similarity_evolution": similarity_evolution,
        "final_similarity":     final_similarity,
        "society":              society,
        "num_rounds":           num_rounds,
        "num_generations":      num_generations,
        "timestamp":            datetime.now().isoformat(),
    }
