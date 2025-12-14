import pandas as pd
import pickle
import os

# =========================
# 경로 설정
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, r"C:\Users\jwm02\OneDrive\바탕 화면\애완동물 관리\data\aihub_pet_data.csv")  # 실제 CSV 경로 확인
OUTPUT_PATH = os.path.join(BASE_DIR, "feature_defaults.pkl")

# =========================
# 데이터 로드
# =========================
df = pd.read_csv(DATA_PATH)

# =========================
# 기본값 계산
# =========================
FEATURE_DEFAULTS = {
    "exercise": df["exercise"].mean(),

    # 사료/간식은 중앙값/상위분위가 안정적
    "food_amount": df["food_amount"].median(),
    "snack_amount": df["snack_amount"].quantile(0.75),
    "food_count": df["food_count"].median(),
}

# =========================
# NaN 방지
# =========================
for k, v in FEATURE_DEFAULTS.items():
    if pd.isna(v):
        raise ValueError(f"{k} 계산 결과가 NaN 입니다.")

# =========================
# 저장
# =========================
with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(FEATURE_DEFAULTS, f)

print("✅ feature_defaults.pkl 생성 완료")
print(FEATURE_DEFAULTS)
