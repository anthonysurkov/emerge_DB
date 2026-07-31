import subprocess
import psycopg2

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
    try:
        conn = psycopg2.connect("postgresql://localhost/emerge")
        conn.close()
        return True
    except psycopg2.OperationalError:
        return False

