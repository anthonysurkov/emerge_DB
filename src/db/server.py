import subprocess
import psycopg2

# Start/stop the Postgres server via brew services.
# Call start() once at the beginning of a session, stop() when done.
# Postgres is cheap to leave running, so stop() is optional.

def start():
    subprocess.run(["brew", "services", "start", "postgresql"])

def stop():
    subprocess.run(["brew", "services", "stop", "postgresql"])

def status():
    result = subprocess.run(
        ["brew", "services", "info", "postgresql"],
        capture_output=True, text=True
    )
    print(result.stdout)

def ping() -> bool:
    # Returns True if the server is running and the emerge db is reachable.
    try:
        conn = psycopg2.connect("postgresql://localhost/emerge")
        conn.close()
        return True
    except psycopg2.OperationalError:
        return False

def is_busy() -> bool:
    # Returns True if any query is actively executing on the emerge db.
    # Uses pg_stat_activity, a built-in Postgres view of current connections.
    # state = 'active' means a query is running (vs. 'idle' = connected but idle).
    with psycopg2.connect("postgresql://localhost/emerge") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM pg_stat_activity
                WHERE state = 'active' AND datname = 'emerge'
            """)
            return cur.fetchone()[0] > 0
