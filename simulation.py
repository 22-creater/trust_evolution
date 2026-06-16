"""
simulation.py - 게임 이론 엔진 + 전략 클래스 (수정본)
"""
import numpy as np
from collections import defaultdict
from datetime import datetime

# ─────────────────────────────────────────────
# 전략 클래스 (Simpleton 삭제)
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

# ─────────────────────────────────────────────
# 상수 (Simpleton 제거, 비율 업데이트)
# ─────────────────────────────────────────────

STRATEGY_MAP = {
    "Always Cooperate": AlwaysCooperate,
    "Always Cheat":     AlwaysCheat,
    "Copycat":          Copycat,
    "Grudger":          Grudger,
    "Detective":        Detective,
}

COUNTRY_PRESETS = {
    "한국 (MBTI 기반)": {"Always Cooperate": 32, "Always Cheat": 7, "Copycat": 20, "Grudger": 13, "Detective": 28},
    "일본 (MBTI 기반)": {"Always Cooperate": 37, "Always Cheat": 6, "Copycat": 17, "Grudger": 14, "Detective": 26},
    "중국 (MBTI 기반)": {"Always Cooperate": 26, "Always Cheat": 8, "Copycat": 24, "Grudger": 13, "Detective": 29},
    "미국 (MBTI 기반)": {"Always Cooperate": 36, "Always Cheat": 7, "Copycat": 21, "Grudger": 11, "Detective": 25},
    "균등 분포":        {"Always Cooperate": 20, "Always Cheat": 20, "Copycat": 20, "Grudger": 20, "Detective": 20},
}

# (나머지 play_match, analyze_ai_behavior, run_simulation 함수는 기존과 동일하게 유지)
