from app.db import get_connection

def save_bcs(
    user_id,
    weight,
    age,
    breed,
    sex,
    exercise,
    food_amount,
    snack_amount,
    food_count,
    bcs_value
):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO bcs_history (
                    user_id,
                    weight,
                    age,
                    breed,
                    sex,
                    exercise,
                    food_amount,
                    snack_amount,
                    food_count,
                    bcs_value
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                user_id,
                weight,
                age,
                breed,
                sex,
                exercise,
                food_amount,
                snack_amount,
                food_count,
                bcs_value
            ))

        conn.commit()
    finally:
        conn.close()
        
def fetch_bcs_history_by_user(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT bcs_value, created_at
                FROM bcs_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id,))
            rows = cur.fetchall()

            # 🔥 최신 → 과거 순서라서, 그래프용으로 뒤집기
            return list(reversed(rows))
    finally:
        conn.close()



        
def fetch_latest_bcs_by_user(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT bcs_value, created_at
                FROM bcs_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            row = cur.fetchone()
            return row   # ✅ dict or None
    finally:
        conn.close()

# 🔥 새로 추가
def fetch_latest_bcs_value_by_user(user_id: int):
    """
    추천/로직 전용
    return: int | None
    """
    row = fetch_latest_bcs_by_user(user_id)

    if row is None:
        return None

    return int(row["bcs_value"])

