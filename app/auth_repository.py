from app.db import get_connection
import bcrypt

def create_user(email: str, password: str):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                (email, pw_hash)
            )
        conn.commit()   # 🔥 이 줄이 핵심
        return True
    except Exception as e:
        conn.rollback()
        print("❌ 회원가입 실패:", e)
        return False
    finally:
        conn.close()



def authenticate_user(email: str, password: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash FROM users WHERE email=%s",
                (email,)
            )
            user = cur.fetchone()

        if not user:
            return None

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return user["id"]   # ✅ int

        return None
    finally:
        conn.close()
