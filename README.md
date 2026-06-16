# 🤖 신뢰의 진화 - AI 학습 시뮬레이션

게임 이론 기반 강화학습 에이전트의 전략 진화를 시각화하는 Streamlit 웹 앱

## 📁 파일 구조

```
trust_evolution_app/
├─ app.py              # Streamlit 메인 UI
├─ db.py               # Supabase 연동 (실험 결과 CRUD)
├─ simulation.py       # 게임 이론 엔진
├─ requirements.txt    # 패키지 목록
└─ .streamlit/
   └─ secrets.toml     # Supabase 인증 정보 (아래 참조)
```

## 🚀 로컬 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Supabase 설정

#### 2-1. Supabase 프로젝트 생성
1. https://supabase.com 접속
2. 새 프로젝트 생성
3. Settings > API > Project URL, anon public key 복사

#### 2-2. 테이블 생성
SQL Editor에서 아래 SQL 실행:

```sql
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    preset_name TEXT NOT NULL,
    society JSONB NOT NULL,
    num_rounds INTEGER NOT NULL,
    num_generations INTEGER NOT NULL,
    final_ai_score NUMERIC(10, 2),
    final_social_score NUMERIC(10, 2),
    generation_scores JSONB,
    strategy_scores JSONB,
    social_scores JSONB,
    similarity_evolution JSONB,
    final_similarity JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_experiments_created ON experiments(created_at DESC);
CREATE INDEX idx_experiments_preset ON experiments(preset_name);
```

#### 2-3. secrets.toml 설정
`.streamlit/secrets.toml` 파일 생성:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### 3. 앱 실행
```bash
streamlit run app.py
```

## 🎨 주요 기능

### 1️⃣ 새 시뮬레이션
- **나라별 MBTI 프리셋**: 한국/일본/중국/미국/균등 분포
- **전략별 인구 조정**: 6가지 전략의 개체수 설정
- **환경 파라미터**: 매치당 라운드, 학습 세대 수
- **실시간 모니터링**: 진행률, AI 점수, 사회 평균 추이

### 2️⃣ 결과 분석
- **점수 추이 그래프**: AI vs 사회 평균 비교
- **행동 패턴 매트릭스**: 상대별 전략 유사도 히트맵
- **사회 구성 분석**: 파이 차트 + 전략별 상세 정보

### 3️⃣ 실험 기록
- **결과 저장**: Supabase에 자동 저장
- **과거 실험 조회**: 저장된 실험 목록 탐색
- **비교 분석**: 여러 실험 간 결과 비교

## 📊 전략 설명

| 전략 | 이모지 | 설명 |
|------|--------|------|
| Always Cooperate | 🤝 | 무조건 협력. 착하지만 착취당하기 쉬움 |
| Always Cheat | 😈 | 무조건 배신. 단기 이익, 장기 신뢰 손실 |
| Copycat | 🐱 | 상대의 이전 행동을 그대로 따라함 (눈에는 눈) |
| Grudger | 😠 | 한 번 배신당하면 영원히 복수 |
| Detective | 🕵️ | 처음 4턴 테스트 후 적응형 대응 |
| Simpleton | 😊 | 협력엔 유지, 배신엔 변경 |
| **Adaptive AI** | 🤖 | 강화학습으로 최적 전략 학습 |

## 🎯 디자인 특징

- **모던 카드 레이아웃**: 그림자 + 호버 효과
- **그라데이션 배경**: 따뜻한 오프화이트 베이스
- **반응형 차트**: matplotlib + koreanize-matplotlib
- **실시간 업데이트**: 자동 리프레시 (시뮬레이션 실행 중)

## 📦 배포 (Streamlit Cloud)

1. GitHub 레포지토리 생성 및 파일 업로드
2. https://streamlit.io/cloud 접속
3. New app > GitHub repo 연결
4. Advanced settings > Secrets 추가:
   ```
   SUPABASE_URL = "..."
   SUPABASE_KEY = "..."
   ```
5. Deploy 클릭

## 🛠 기술 스택

- **Frontend**: Streamlit (Python 웹 프레임워크)
- **Backend**: Supabase (PostgreSQL 기반 BaaS)
- **Simulation**: NumPy (강화학습 Q-learning)
- **Visualization**: Matplotlib + koreanize-matplotlib

## 📝 라이선스

MIT License

---

**Made with ❤️ for AI & Game Theory Research**
