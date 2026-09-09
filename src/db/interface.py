import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from pathlib import Path


# CORE
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


# AUTHOR I/O
def get_authors() -> list:
    return [row["author"] for row in db_query("SELECT author FROM author_info")]

def insert_author(author: str, email: str) -> None:
    db_query(
        "INSERT INTO author_info (author, email)"
        "VALUES (%s, %s)"
        "ON CONFLICT (author) DO UPDATE SET email = EXCLUDED.email",
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


# SEQUENCE I/O
def get_target_ids() -> list[str]:
    rows = db_query("SELECT target_id FROM hairpin_info")
    return [row["target_id"] for row in rows]

def insert_hairpin_info(
    target_id: str,
    hairpin_seq: str,
    edit_A_idx: int,
    edit_reg_start: int,
    edit_reg_end: int,
    var_reg_start: int,
    var_reg_end: int
) -> bool:
    try:
        db_query("INSERT INTO hairpin_info (target_id, hairpin_seq, "
            "edit_a_idx, edit_region_start, edit_region_end, var_region_start, "
            "var_region_end) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                target_id, hairpin_seq,
                edit_A_idx, edit_reg_start, edit_reg_end,
                var_reg_start, var_reg_end,
            )
        )
    except psycopg2.Error:
        return False
    return True


# SCREEN I/O
def insert_screen_metadata(
    author: str,
    processing_date: str,
    submission_date: str | None,
    tid: str,
    forward_primer: str,
    reverse_primer: str,
    r1_path: str,
    r2_path: str,
    num_reads_ordered: int,
) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO screen_metadata (
                    target_id,
                    author,
                    submission_date,
                    num_reads_ordered,
                    forward_primer,
                    reverse_primer,
                    processing_date,
                    r1_path,
                    r2_path
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING screen_id
                """,
                (
                    tid,
                    author,
                    submission_date,
                    num_reads_ordered,
                    forward_primer,
                    reverse_primer,
                    processing_date,
                    r1_path,
                    r2_path,
                ),
            )
            screen_id = cur.fetchone()[0]
        conn.commit()

    return screen_id

def insert_emerge_data(screen_id: int, seq: str, n: int, k: int, mle: float):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO emerge_data (screen_id, seq, n, k, mle) VALUES "
                "(%s, %s, %s, %s, %s)",
                (screen_id, seq, n, k, mle)
            )
        conn.commit()

def get_screens_overview() -> dict[int, str]:
    screen_ids = db_query("SELECT DISTINCT screen_id FROM emerge_data")
    ids = tuple(row["screen_id"] for row in screen_ids)
    if not ids:
        return None
    target_ids = db_query(
        "SELECT target_id, author FROM screen_metadata "
        "WHERE screen_id IN %s",
        (ids,)
    )
    if target_ids is None:
        return None
    return dict(zip(screen_ids, target_ids))

def get_screens_by_metadata(
    authors: list[str] = None,
    target_ids: list[str] = None,
    seqs: list[str] = None
) -> pd.DataFrame:
    conditions = []
    params = []

    if authors:
        conditions.append("sm.author = ANY(%s)")
        params.append(authors)
    if target_ids:
        conditions.append("sm.target_id = ANY(%s)")
        params.append(target_ids)
    if seqs:
        conditions.append("ed.seq = ANY(%s)")
        params.append(seqs)

    where_clause = (
        f"WHERE {' AND '.join(conditions)}"
        if conditions
        else ""
    )
    query = f"""
        SELECT sm.author, sm.target_id,
               ed.screen_id, ed.seq, ed.n, ed.k, ed.mle
        FROM emerge_data AS ed
        JOIN screen_metadata AS sm
          ON sm.screen_id = ed.screen_id
        {where_clause}
        ORDER BY ed.screen_id, ed.id
    """
    rows = db_query(query, tuple(params))
    return pd.DataFrame(data=rows)


# METHOD I/O
def insert_method_info(
    method_name: str,
    method_path: Path,
    method_desc: str | None = None,
    method_writeup_path: Path | None = None
) -> None:
    if not method_path.exists():
        raise ValueError("method_path provided does not exist")
    if method_writeup_path is not None and not method_writeup_path.exists():
        raise ValueError("method_writeup_path provided does not exist")

    try:
        db_query(
            "INSERT INTO methods_info"
            "(method_name, method_path, method_desc, method_writeup_path)"
            "VALUES (%s, %s, %s, %s)",
            (
                method_name, str(method_path),
                method_desc, str(method_writeup_path),
            )
        )
        return True
    except Exception:
        return False

def remove_method(method_name: str) -> bool:
    try:
        db_query(
            "DELETE FROM methods_info WHERE method_name = (%s)",
            (method_name,)
        )
        return True
    except psycopg2.errors.ForeignKeyViolation:
        return False

def update_method_desc(method_name: str, method_desc: str) -> None:
    try:
        db_query(
            "UPDATE methods_info SET method_desc = (%s) WHERE method_name = (%s)",
            (method_desc, method_name,)
        )
        return True
    except Exception:
        return False

def update_method_writeup(method_name: str, method_writeup_path: str) -> None:
    try:
        db_query(
            "UPDATE methods_info SET method_writeup_path = (%s)"
            "WHERE method_name = (%s)",
            (method_writeup_path, method_name,)
        )
        return True
    except Exception:
        return False

def get_method_names() -> list[str]:
    rows = db_query("SELECT method_name FROM methods_info")
    return [row["method_name"] for row in rows]

def get_method_info(method_name: str) -> dict[str, str, str, str]:
    return db_query_one(
        "SELECT * FROM methods_info WHERE method_name = (%s)",
        (method_name,)
    )
