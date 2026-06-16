"""
simulation.py - 게임 이론 시뮬레이션 엔진
"""

import numpy as np
from collections import defaultdict
from datetime import datetime

class Strategy:
    def __init__(self, name, description, emoji):
        self.name = name
        self.description = description
        self.emoji = emoji
        self.reset()

    def reset(self):
        pass

    def decide(self, opponent_history):
        raise NotImplementedError

class AlwaysCooperate(Strategy):
    def __init__(self):
        super().__init__("Always Cooperate", "무조건 협력합니다. 착하지만 착취당하기 쉬워요.", "🤝")
    def decide(self, opponent_history): 
        return True

class AlwaysCheat(Strategy):
    def __init__(self):
        super().__init__("Always Cheat", "무조건 배신합니다. 단기적으로 유리하지만 신뢰를 잃어요.", "😈")
    def decide(self, opponent_history): 
        return False

class Copycat(Strategy):
    def __init__(self):
        super().__init__("Copycat", "눈에는 눈! 상대방의 이전 행동을 그대로 따라합니다.", "🐱")
    def decide(self, opponent_history):
        if len(opponent_history) == 0: 
            return True
        return opponent_history[-1]

class Grudger(Strategy):
    def __init__(self):
        super().__init__("Grudger", "한 번 배신당하면 영원히 복수합니다. 용서는 없어요!", "😠")
    def reset(self): 
        self.betrayed = False
    def decide(self, opponent_history):
        if self.betrayed: 
            return False
        if len(opponent_history) > 0 and not opponent_history[-1]:
            self.betrayed = True
            return False
        return True

class Detective(Strategy):
    def __init__(self):
        super().__init__("Detective", "처음 4턴으로 상대를 테스트: 한 번도 안 속이면 착취, 배신하면 Copycat으로 대응합니다.", "🕵️")
    def reset(self):
        self.turn = 0
        self.opponent_cheated = False
    def decide(self, opponent_history):
        self.turn += 1
        if self.turn <= 4:
            return [True, False, True, True][self.turn - 1]
        if self.turn == 5 and len(opponent_history) >= 4:
            self.opponent_cheated = not all(opponent_history[:4])
        if self.turn > 4:
            if self.opponent_cheated:
                return opponent_history[-1] if opponent_history else True
            else:
                return False
        return True

class Simpleton(Strategy):
    def __init__(self):
        super().__init__("Simpleton", "상대가 협력하면 같은 행동을, 배신하면 행동을 바꿉니다.", "😊")
    def reset(self): 
        self.last_move = True
    def decide(self, opponent_history):
        if len(opponent_history) == 0: 
            return True
        if opponent_history[-1]: 
            next_move = self.last_move
        else: 
            next_move = not self.last_move
        self.last_move = next_move
        return next_move

class AdaptiveAI(Strategy):
    def __init__(self, learning_rate=0.1, discount=0.95,
                 epsilon_start=0.9, epsilon_end=0.05, epsilon_decay=0.97):
        super().__init__("Adaptive AI", "강화학습으로 최적의 전략을 스스로 찾아갑니다.", "🤖")
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.q_table = defaultdict(lambda: [0.0, 0.0])
        self.reset()

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def reset(self):
        self.last_state = None
        self.last_action = None

    def get_state(self, opponent_history):
        if len(opponent_history) == 0: 
            return "start"
        return tuple(opponent_history[-3:])

    def decide(self, opponent_history):
        state = self.get_state(opponent_history)
        if np.random.random() < self.epsilon:
            action = np.random.choice([True, False])
        else:
            q_values = self.q_table[state]
            action = True if q_values[0] >= q_values[1] else False
        self.last_state = state
        self.last_action = action
        return action

    def update(self, reward, opponent_history):
        if self.last_state is None: 
            return
        current_state = self.get_state(opponent_history)
        action_idx = 0 if self.last_action else 1
        current_q = self.q_table[self.last_state][action_idx]
        max_next_q = max(self.q_table[current_state])
        self.q_table[self.last_state][action_idx] = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)

STRATEGY_MAP = {
    "Always Cooperate": AlwaysCooperate,
    "Always Cheat": AlwaysCheat,
    "Copycat": Copycat,
    "Grudger": Grudger,
    "Detective": Detective,
    "Simpleton": Simpleton
}

COUNTRY_PRESETS = {
    "한국 (MBTI 기반)": {"Always Cooperate": 16, "Always Cheat": 6, "Copycat": 16, "Grudger": 5, "Detective": 9, "Simpleton": 8},
    "일본 (MBTI 기반)": {"Always Cooperate": 16, "Always Cheat": 5, "Copycat": 18, "Grudger": 4, "Detective": 9, "Simpleton": 7},
    "중국 (MBTI 기반)": {"Always Cooperate": 19, "Always Cheat": 7, "Copycat": 12, "Grudger": 5, "Detective": 8, "Simpleton": 9},
    "미국 (MBTI 기반)": {"Always Cooperate": 18, "Always Cheat": 6, "Copycat": 17, "Grudger": 5, "Detective": 8, "Simpleton": 6},
    "균등 분포": {"Always Cooperate": 10, "Always Cheat": 10, "Copycat": 10, "Grudger": 10, "Detective": 10, "Simpleton": 10}
}

def play_round(strategy1, strategy2, history1, history2):
    move1 = strategy1.decide(history2)
    move2 = strategy2.decide(history1)
    if move1 and move2: 
        reward1, reward2 = 2, 2
    elif move1 and not move2: 
        reward1, reward2 = 0, 3
    elif not move1 and move2: 
        reward1, reward2 = 3, 0
    else: 
        reward1, reward2 = 1, 1
    return move1, move2, reward1, reward2

def play_match(strategy1, strategy2, rounds=100):
    strategy1.reset()
    strategy2.reset()
    history1, history2 = [], []
    score1, score2 = 0, 0
    for _ in range(rounds):
        move1, move2, reward1, reward2 = play_round(strategy1, strategy2, history1, history2)
        history1.append(move1)
        history2.append(move2)
        score1 += reward1
        score2 += reward2
        if isinstance(strategy1, AdaptiveAI): 
            strategy1.update(reward1, history2)
        if isinstance(strategy2, AdaptiveAI): 
            strategy2.update(reward2, history1)
    return score1, score2

def analyze_ai_behavior(ai, rounds=100):
    strategy_classes = {
        "Always Cooperate": AlwaysCooperate,
        "Always Cheat": AlwaysCheat,
        "Copycat": Copycat,
        "Grudger": Grudger,
        "Detective": Detective,
        "Simpleton": Simpleton,
    }

    ai_sequences = {}
    for opp_name, OppClass in strategy_classes.items():
        opponent = OppClass()
        ai.reset()
        opponent.reset()
        h_ai, h_opp = [], []
        seq = []
        for _ in range(rounds):
            move_ai = ai.decide(h_opp.copy())
            move_opp = opponent.decide(h_ai.copy())
            if move_ai and move_opp: r_ai = 2
            elif move_ai and not move_opp: r_ai = 0
            elif not move_ai and move_opp: r_ai = 3
            else: r_ai = 1
            h_ai.append(move_ai)
            h_opp.append(move_opp)
            seq.append(move_ai)
            if isinstance(ai, AdaptiveAI):
                ai.update(r_ai, h_opp)
        ai_sequences[opp_name] = seq

    ref_sequences = {}
    for ref_name, RefClass in strategy_classes.items():
        ref_sequences[ref_name] = {}
        for opp_name, OppClass in strategy_classes.items():
            ref = RefClass()
            opponent = OppClass()
            ref.reset()
            opponent.reset()
            h_ref, h_opp = [], []
            seq = []
            for _ in range(rounds):
                move_ref = ref.decide(h_opp.copy())
                move_opp = opponent.decide(h_ref.copy())
                h_ref.append(move_ref)
                h_opp.append(move_opp)
                seq.append(move_ref)
            ref_sequences[ref_name][opp_name] = seq

    matrix = {}
    for ref_name in strategy_classes:
        matrix[ref_name] = {}
        for opp_name in strategy_classes:
            ai_seq = ai_sequences[opp_name]
            ref_seq = ref_sequences[ref_name][opp_name]
            matches = sum(a == r for a, r in zip(ai_seq, ref_seq))
            matrix[ref_name][opp_name] = round(matches / rounds * 100, 1)

    return matrix

def run_simulation(society, num_rounds, num_generations, progress_callback=None):
    """
    시뮬레이션 실행 (콜백으로 진행상황 전달)
    """
    population = []
    for strategy_name, count in society.items():
        for _ in range(count):
            population.append(STRATEGY_MAP[strategy_name]())

    ai = AdaptiveAI(learning_rate=0.1, discount=0.95, epsilon_start=0.9, epsilon_end=0.05, epsilon_decay=0.97)
    generation_scores = []
    social_scores = []
    strategy_scores = defaultdict(list)
    similarity_evolution = []

    analysis_points = [0, num_generations//4, num_generations//2, 3*num_generations//4, num_generations-1]

    for gen in range(num_generations):
        total_ai_score = 0
        total_npc_score = 0
        gen_strategy_scores = defaultdict(lambda: {"ai": 0, "count": 0})

        for npc in population:
            ai_score, npc_score = play_match(ai, npc, num_rounds)
            total_ai_score += ai_score
            total_npc_score += npc_score
            gen_strategy_scores[npc.name]["ai"] += ai_score
            gen_strategy_scores[npc.name]["count"] += 1

        avg_ai_score = total_ai_score / len(population)
        avg_social_score = (total_ai_score + total_npc_score) / (len(population) * 2)
        generation_scores.append(avg_ai_score)
        social_scores.append(avg_social_score)

        for strategy_name, scores in gen_strategy_scores.items():
            strategy_scores[strategy_name].append(scores["ai"] / scores["count"])

        ai.decay_epsilon()

        if gen in analysis_points:
            similarity = analyze_ai_behavior(ai)
            similarity_evolution.append((gen, similarity))

        if progress_callback:
            progress_callback(gen + 1, num_generations, avg_ai_score, avg_social_score)

    final_similarity = analyze_ai_behavior(ai)

    return {
        "generation_scores": generation_scores,
        "strategy_scores": dict(strategy_scores),
        "social_scores": social_scores,
        "similarity_evolution": similarity_evolution,
        "final_similarity": final_similarity,
        "society": society,
        "num_rounds": num_rounds,
        "num_generations": num_generations,
        "timestamp": datetime.now().isoformat()
    }
