# app/recommend/feed_faiss.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def rerank_feeds_with_faiss(feeds, query, top_k=5):
    """
    feeds: 네이버 쇼핑 결과 리스트
    query: 예) "강아지 체중관리 사료"
    """

    texts = []
    valid_feeds = []

    for f in feeds:
        text = f"{f.get('title','')} {f.get('description','')}"
        if text.strip():
            texts.append(text)
            valid_feeds.append(f)

    if not texts:
        return feeds[:top_k]

    # 임베딩
    feed_emb = model.encode(texts, convert_to_numpy=True)
    query_emb = model.encode([query], convert_to_numpy=True)

    dim = feed_emb.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine 유사도
    faiss.normalize_L2(feed_emb)
    faiss.normalize_L2(query_emb)

    index.add(feed_emb)
    scores, idxs = index.search(query_emb, top_k)

    return [valid_feeds[i] for i in idxs[0]]
