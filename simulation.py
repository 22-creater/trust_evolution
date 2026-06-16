# ─────────────────────────────────────────────
# 전략 클래스 (Simpleton 삭제)
# ─────────────────────────────────────────────

# ... (기존 AlwaysCooperate, AlwaysCheat, Copycat, Grudger, Detective 유지)

# Simpleton 클래스 삭제됨

# ─────────────────────────────────────────────
# 상수 수정
# ─────────────────────────────────────────────

STRATEGY_MAP = {
    "Always Cooperate": AlwaysCooperate,
    "Always Cheat":     AlwaysCheat,
    "Copycat":          Copycat,
    "Grudger":          Grudger,
    "Detective":        Detective,
    # "Simpleton": 삭제됨
}

# 방금 계산한 16개 유형 합산 비율 적용 (비율을 인구 수로 설정)
COUNTRY_PRESETS = {
    "한국 (MBTI 기반)": {"Always Cooperate": 32, "Always Cheat": 7, "Copycat": 20, "Grudger": 13, "Detective": 28},
    "일본 (MBTI 기반)": {"Always Cooperate": 37, "Always Cheat": 6, "Copycat": 17, "Grudger": 14, "Detective": 26},
    "중국 (MBTI 기반)": {"Always Cooperate": 26, "Always Cheat": 8, "Copycat": 24, "Grudger": 13, "Detective": 29},
    "미국 (MBTI 기반)": {"Always Cooperate": 36, "Always Cheat": 7, "Copycat": 21, "Grudger": 11, "Detective": 25},
    "균등 분포":        {"Always Cooperate": 20, "Always Cheat": 20, "Copycat": 20, "Grudger": 20, "Detective": 20},
}
