import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect("postgresql://localhost/emerge")

def db_query(query: str, params: tuple = ()) -> dict:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()

def get_screen(screen_id: int) -> dict:
    return db_query(
        "SELECT * FROM screen_metadata "
        "WHERE screen_id = %s",
        (screen_id,)
    )

def insert_emerge_data(screen_id: int, seq: str, n: int, k: int, mle: float):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO emerge_data (screen_id, seq, n, k, mle) VALUES "
                "(%s, %s, %s, %s, %s)",
                (screen_id, seq, n, k, mle)
            )
        conn.commit()
