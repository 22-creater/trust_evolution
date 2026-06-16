"""
db.py - Supabase 연동 레이어 (실험 결과 저장/불러오기)
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import json

@st.cache_resource
def get_supabase_client() -> Client:
    """Supabase 클라이언트 싱글톤"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def init_db():
    """
    Supabase SQL Editor에서 아래 SQL을 한 번만 실행하세요:

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
    """
    pass

def save_experiment(preset_name: str, results: dict) -> bool:
    """실험 결과 저장"""
    try:
        client = get_supabase_client()

        data = {
            "preset_name": preset_name,
            "society": json.dumps(results["society"]),
            "num_rounds": results["num_rounds"],
            "num_generations": results["num_generations"],
            "final_ai_score": float(results["generation_scores"][-1]) if results["generation_scores"] else 0,
            "final_social_score": float(results["social_scores"][-1]) if results["social_scores"] else 0,
            "generation_scores": json.dumps(results["generation_scores"]),
            "strategy_scores": json.dumps(results["strategy_scores"]),
            "social_scores": json.dumps(results["social_scores"]),
            "similarity_evolution": json.dumps([(gen, matrix) for gen, matrix in results["similarity_evolution"]]),
            "final_similarity": json.dumps(results["final_similarity"]),
        }

        client.table("experiments").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"저장 실패: {str(e)}")
        return False

def load_experiments(limit=20):
    """최근 실험 목록 불러오기"""
    try:
        client = get_supabase_client()
        resp = client.table("experiments") \
            .select("id, preset_name, num_rounds, num_generations, final_ai_score, final_social_score, created_at") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return resp.data
    except Exception as e:
        st.error(f"불러오기 실패: {str(e)}")
        return []

def load_experiment_detail(experiment_id: int):
    """특정 실험의 상세 데이터 불러오기"""
    try:
        client = get_supabase_client()
        resp = client.table("experiments") \
            .select("*") \
            .eq("id", experiment_id) \
            .single() \
            .execute()

        data = resp.data

        # JSON 필드 파싱
        return {
            "id": data["id"],
            "preset_name": data["preset_name"],
            "society": json.loads(data["society"]),
            "num_rounds": data["num_rounds"],
            "num_generations": data["num_generations"],
            "generation_scores": json.loads(data["generation_scores"]),
            "strategy_scores": json.loads(data["strategy_scores"]),
            "social_scores": json.loads(data["social_scores"]),
            "similarity_evolution": [(gen, matrix) for gen, matrix in json.loads(data["similarity_evolution"])],
            "final_similarity": json.loads(data["final_similarity"]),
            "created_at": data["created_at"]
        }
    except Exception as e:
        st.error(f"상세 불러오기 실패: {str(e)}")
        return None

def delete_experiment(experiment_id: int) -> bool:
    """실험 삭제"""
    try:
        client = get_supabase_client()
        client.table("experiments").delete().eq("id", experiment_id).execute()
        return True
    except Exception as e:
        st.error(f"삭제 실패: {str(e)}")
        return False
