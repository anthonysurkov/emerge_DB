import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect("postgresql://localhost/emerge")

def db_query(query: str, params: tuple = ()) -> dict | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall() if cur.description else None

def db_query_one(query: str, params: tuple = ()) -> dict | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone() if cur.description else None

# AUTHOR MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def get_authors() -> list:
    return [row["author"] for row in db_query("SELECT author FROM author_info")]

def insert_author(author: str, email: str) -> None:
    db_query(
        "INSERT INTO author_info (author, email) VALUES (%s, %s)",
        (author, email,)
    )

def remove_author(author: str) -> bool:
    try:
        db_query(
            "DELETE FROM author_info WHERE author = %s",
            (author,)
        )
        return True
    except psycopg2.errors.ForeignKeyViolation:
        return False

# SEQUENCE MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def get_sequence_ids() -> list[str]:
    return db_query("SELECT sequence_id FROM sequence_info")

def insert_sequence_info(
    sequence_id: str,
    hairpin_seq: str,
    edit_A_idx: int,
    edit_reg_start: int,
    edit_reg_end: int,
    var_reg_start: int,
    var_reg_end: int
) -> bool:
    try:
        db_query("INSERT INTO sequence_info (sequence_id, hairpin_seq, "
            "edit_a_idx, edit_region_start, edit_region_end, var_region_start, "
            "var_region_end) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (sequence_id, hairpin_seq,
                edit_A_idx, edit_reg_start, edit_reg_end,
                var_reg_start, var_reg_end,
            )
        )
    except psycopg2.Error:
        return False
    return True

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
