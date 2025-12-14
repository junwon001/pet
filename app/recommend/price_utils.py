import re

def extract_weight_kg(title: str) -> float | None:
    """
    예: "10kg", "2.72kg", "7.5kg"
    """
    match = re.search(r'(\d+(\.\d+)?)\s*kg', title.lower())
    if match:
        return float(match.group(1))
    return None

def price_per_kg(price: int, weight_kg: float) -> float:
    return price / weight_kg

def value_score(price: int, weight_kg: float) -> float:
    """
    값이 높을수록 가성비 좋음
    """
    return weight_kg / price
