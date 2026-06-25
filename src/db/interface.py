import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect("postgresql://localhost/emerge")

def db_query(query: str, params: tuple = ()) -> dict:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

# AUTHOR MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def get_authors() -> list:
    return [row["author"] for row in db_query("SELECT author FROM author_info")]

def insert_author(author: str, email: str) -> None:
    db_query(
        "INSERT INTO author_info (author, email) VALUES (%s, %s)",
        (author, email,)
    )

def remove_author(author: str) -> None:
    db_query(
        "DELETE FROM author_info WHERE author = %s",
        (author,)
    )

# SCREEN MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def get_screen(screen_id: int) -> dict:
    rows = db_query(
        "SELECT * FROM screen_metadata WHERE screen_id = %s",
        (screen_id,)
    )
    return rows[0] if rows else None

def insert_emerge_data(screen_id: int, seq: str, n: int, k: int, mle: float):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO emerge_data (screen_id, seq, n, k, mle) VALUES "
                "(%s, %s, %s, %s, %s)",
                (screen_id, seq, n, k, mle)
            )
        conn.commit()
