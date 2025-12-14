from app.recommend.recommend_logic import (
    bcs_to_feed_type,
    feed_type_to_query
)
from app.recommend.feed_catalog import search_feed_from_naver
from app.recommend.feed_embedding import get_similar_items
from app.recommend.bcs_explainer import explain_bcs
from app.bcs_repository import fetch_latest_bcs_value_by_user
from app.recommend.feed_faiss import rerank_feeds_with_faiss

from app.recommend.recommend_logic import generate_feed_reason

def recommend_feed_by_bcs(user_id: int):
    try:
        # ✅ 반드시 value 전용 함수 사용
        bcs = fetch_latest_bcs_value_by_user(user_id)

        if bcs is None:
            return {"error": "BCS 기록 없음"}

        feed_type = bcs_to_feed_type(bcs)
        query = feed_type_to_query(feed_type)

        feeds = search_feed_from_naver(query=query, display=10)

        ranked_feeds = get_similar_items(
            feeds=feeds,
            query=query,
            top_k=5
        )

        for feed in ranked_feeds:
            feed["recommend_reason"] = generate_feed_reason(
                feed_type,
                feed_title=feed["title"]
            )

        return {
            "user_id": user_id,
            "bcs": bcs,
            "feed_type": feed_type,
            "recommended_feeds": ranked_feeds
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }


    

