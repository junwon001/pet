# 품종 평균 체중 (간단 버전)
BREED_AVG_WEIGHT = {
    "비글": 10.0,
    "비숑프리제": 6.5,
    "불독": 24.0,
    "치와와 장모": 2.25,
    "치와와 단모": 2.25,
    "코카스패니얼": 13.0,
    "닥스훈트 장모": 11.5,
    "닥스훈트 단모": 11.5,
    "도베르만 핀셔": 39.5,
    "골든리트리버": 31.5,
    "시추": 5.5,
    "저먼셰퍼드": 35.0,
    "그레이트피레니즈": 55.0,
    "하운드": 35.0,
    "허스키": 23.5,
    "진도": 21.5,
    "래브라도리트리버": 32.5,
    "몰티즈": 3.0,
    "믹스 장모": "N/A",
    "믹스 단모": "N/A",
    "말라뮤트": 40.5,
    "포메라니안": 2.65,
    "푸들": 16.5,
    "슈나우저": 12.5,
    "쉽독": 18.0,
    "테리어": 16.5,
    "웰시코기": 12.0,
    "코리안숏헤어": 5.0,
    "페르시안": 4.5,
    "러시안블루": 5.0,
    "스코티시폴드": 4.5,
    "샴": 5.0,
    "터키시앙고라": 4.0
   
}

def apply_underweight_rule(
    predicted_bcs: int,
    weight: float,
    age: int,
    breed: str,
    food_amount: float | None,
    exercise: float | None
) -> int:

    avg_weight = BREED_AVG_WEIGHT.get(breed)
    if not avg_weight:
        return predicted_bcs

    score = 0

    if weight < avg_weight * 0.7:
        score += 2

    if food_amount is not None and food_amount < avg_weight * 30:
        score += 1

    if exercise is not None and exercise < 0.3:
        score += 1

    if age >= 7:
        score += 1

    if score >= 2:
        return 2   

    return predicted_bcs
