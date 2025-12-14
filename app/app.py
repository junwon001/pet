from fastapi import FastAPI
from pydantic import BaseModel
from ml.obesity_model import predict_obesity

from app.bcs_repository import save_bcs
from app.utils import extract_bcs_number   # 정규식 함수
from app.bcs_repository import fetch_latest_bcs_by_user
from app.bcs_repository import fetch_bcs_history_by_user 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db import get_connection
from app.auth_repository import create_user, authenticate_user
from fastapi import HTTPException
from app.recommend.recommend_service import recommend_feed_by_bcs
from app.pet_repository import get_pets_by_user
from app.pet_repository import create_pet
from rag.main import generate_answer
from app.bcs_rules import apply_underweight_rule


import os


app = FastAPI(title="Pet Obesity AI API")

# -------------------------
# 웹(static) 설정
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "../web")

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


# -------------------------
# 요청 모델
# -------------------------
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    user_id: int

    weight: float = Field(..., gt=0)
    age: int = Field(..., ge=1)

    breed: str
    sex: str

    exercise: float | None = None
    food_amount: float | None = None
    snack_amount: float | None = None
    food_count: int | None = Field(None, ge=1)



@app.post("/predict")
def predict(req: PredictRequest):
    result = predict_obesity(
        weight=req.weight,
        age=req.age,
        breed=req.breed,
        sex=req.sex,
        exercise=req.exercise,
        food_amount=req.food_amount,
        snack_amount=req.snack_amount,
        food_count=req.food_count
    )

    # ✅ dict에서 직접 꺼낸다
    bcs_value = result.get("bcs")
    
    bcs_value = apply_underweight_rule(
    predicted_bcs=bcs_value,
    weight=req.weight,
    age=req.age,
    breed=req.breed,
    food_amount=req.food_amount,
    exercise=req.exercise
)

    save_bcs(
        user_id=req.user_id,
        weight=req.weight,
        age=req.age,
        breed=req.breed,
        sex=req.sex,
        exercise=req.exercise,
        food_amount=req.food_amount,
        snack_amount=req.snack_amount,
        food_count=req.food_count,
        bcs_value=bcs_value
    )

    return {
        "bcs": bcs_value,
        "raw_result": result
    }   # 그대로 반환
@app.get("/bcs/latest/user/{user_id}")
def get_latest_bcs_api(user_id: int):
    row = fetch_latest_bcs_by_user(user_id)

    if not row:
        return {
            "bcs": None,
            "created_at": None
        }

    return {
        "bcs": row["bcs_value"],             
        "created_at": row["created_at"].isoformat()
    }




@app.get("/bcs/history/user/{user_id}")
def bcs_history_api(user_id: int):
    rows = fetch_bcs_history_by_user(user_id)

    return [
        {
            "bcs": r["bcs_value"],
            "date": r["created_at"].isoformat()
        }
        for r in rows
    ]





class LoginRequest(BaseModel):
    email: str
    password: str
    
class SignupRequest(BaseModel):
    email: str
    password: str
class PetCreateRequest(BaseModel):
    name: str
    species: str
    breed: str
    sex: str
    birth_year: int

from fastapi import HTTPException

@app.post("/signup")
def signup(req: SignupRequest):
    try:
        create_user(req.email, req.password)
        return {"message": "회원가입 성공"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.post("/login")
def login(req: LoginRequest):
    user_id = authenticate_user(req.email, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호 오류")

    return {
        "message": "로그인 성공",
        "user_id": user_id
    }

 
class ConsultRequest(BaseModel):
    question: str
    department: str | None = None   

@app.post("/consult")
def consult(req: ConsultRequest):
    filters = None

    if req.department:
        filters = {"department_meta": req.department}

    answer = generate_answer(
        query=req.question,
        filters=filters
    )

    return {
        "answer": answer
    }





@app.get("/recommend/{user_id}")
def recommend(user_id: int):
    return recommend_feed_by_bcs(user_id)

