# app/user_repository.py

from app.db import get_connection
import bcrypt

def create_user(email: str, password: str):
    conn = None
    try:
        conn = get_connection()

        with conn.cursor() as cur:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            sql = """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            """
            cur.execute(sql, (email, password_hash))

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ 회원가입 실패:", e)
        raise  # 🔥 이거 때문에 FastAPI 콘솔/응답에서 진짜 원인 보임

    finally:
        if conn:
            conn.close()

# app/user_repository.py
def authenticate_user(email: str, password: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )
            user = cur.fetchone()

        if not user:
            return None

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return user

        return None

    finally:
        conn.close()
    