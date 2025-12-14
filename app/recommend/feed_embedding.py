from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import numpy as np

from app.recommend.price_utils import extract_weight_kg
####### 향후 사용
# -------------------------------------------------
# 🔹 한국어 SBERT 모델 로드
# -------------------------------------------------
# 가볍고 한국어 성능 좋은 모델
model = SentenceTransformer(
    "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
)


# -------------------------------------------------
# 🔹 임베딩 유틸 함수
# -------------------------------------------------
def embed_texts(texts: List[str]) -> np.ndarray:
    """
    문자열 리스트 → 임베딩 벡터 (n, dim)
    """
    return model.encode(texts)


# -------------------------------------------------
# 🔹 임베딩 + 가성비 기반 유사 사료 추천
# -------------------------------------------------
def get_similar_items(
    feeds: List[Dict],
    query: str,
    top_k: int = 5
) -> List[Dict]:
    """
    feeds: 네이버 쇼핑 API 결과 리스트
    query: 검색 쿼리 (예: '강아지 다이어트 사료')
    top_k: 최종 추천 개수
    """

    if not feeds:
        return []

    # 1️⃣ 임베딩 대상 텍스트 구성
    texts = [feed["title"] for feed in feeds]

    # 2️⃣ 임베딩 계산
    query_emb = embed_texts([query])   # (1, dim)
    feed_embs = embed_texts(texts)     # (n, dim)

    # 3️⃣ 코사인 유사도 계산
    similarities = cosine_similarity(query_emb, feed_embs)[0]

    scored_items = []

    # 4️⃣ 의미 유사도 + 가성비 결합 점수 계산
    for feed, sim in zip(feeds, similarities):
        title = feed.get("title", "")
        price = feed.get("price")

        weight_kg = extract_weight_kg(title)

        # 가성비 점수 (kg / price)
        if weight_kg and price:
            value_score = weight_kg / price
        else:
            value_score = 0.0

        # 🔥 최종 점수 (의미 + 가성비)
        final_score = float(sim) * (1 + value_score * 100)

        # 결과에 정보 추가
        feed["similarity"] = round(float(sim), 4)
        feed["weight_kg"] = weight_kg
        feed["value_score"] = round(value_score, 6)
        feed["final_score"] = round(final_score, 4)

        scored_items.append(feed)

    # 5️⃣ 점수 기준 정렬
    ranked = sorted(
        scored_items,
        key=lambda x: x["final_score"],
        reverse=True
    )

    return ranked[:top_k]
