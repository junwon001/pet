from app.db import get_connection

def get_pets_by_user(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name FROM pets WHERE user_id=%s",
                (user_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()


def create_pet(user_id: int, data: dict):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pets (user_id, name, species, breed, sex, birth_year)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    data["name"],
                    data["species"],
                    data["breed"],
                    data["sex"],
                    data["birth_year"]
                )
            )
        conn.commit()
        return True
    finally:
        conn.close()

def get_pets_by_user(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM pets WHERE user_id=%s",
                (user_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()
