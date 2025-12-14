def bcs_to_feed_type(bcs):
    if isinstance(bcs, dict):
        bcs = bcs.get("bcs")

    if bcs is None:
        return "normal"
    bcs = int(bcs)  #  방어
    
    if bcs <= 3:
        return "underweight"
    elif 4 <= bcs <= 5:
        return "normal"
    elif 6 <= bcs <= 7:
        return "overweight"   # 🔥 여기
    else:
        return "obese"




def feed_type_to_query(feed_type: str) -> str:
    mapping = {
        "underweight": "강아지 고단백 사료",
        "normal": "강아지 성견 사료",
        "overweight": "강아지 체중관리 사료",
        "obese": "강아지 다이어트 사료"
    }
    return mapping.get(feed_type, "강아지 사료")

def generate_feed_reason(feed_type: str, feed_title: str) -> str:
    reasons = []

    if feed_type == "obese":
        reasons.append("비만 관리에 적합한 저칼로리 사료")
    elif feed_type == "overweight":
        reasons.append("체중 증가 예방을 위한 체중 관리용 사료")
    elif feed_type == "underweight":
        reasons.append("체중 증가를 돕는 고영양 사료")
    else:  # normal
        reasons.append("현재 체형 유지를 위한 균형 잡힌 사료")

    title_lower = feed_title.lower()

    if "다이어트" in feed_title or "weight" in title_lower:
        reasons.append("다이어트 특화 제품")
    if "저지방" in feed_title:
        reasons.append("지방 함량이 낮음")
    if "노령" in feed_title or "시니어" in feed_title:
        reasons.append("노령견에 맞춘 영양 설계")

    return " / ".join(reasons)

