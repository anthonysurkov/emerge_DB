import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path

from db.interface import db_query

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587 # standard client submission port

def email_user(file: Path) -> None:
    recipient = db_query(
        "SELECT a.email "
        "FROM screen_metadata s "
        "JOIN author_info a ON s.author = a.author "
        "WHERE s.rawdata_path = %s",
        (str(file),)
    )["email"]

    if not load_dotenv():
        raise ValueError(
            f".env file not detected in process folder; emailer.py failed"
        )
    USER = os.getenv("USERNAME")
    PASS = os.getenv("PASS")

    msg = MIMEText(f"Dear User,\n\nYour job concerning file "
        f"{file.name} is ready!\n"
        f"(Please do not reply; notification only)\n\n"
        f"Regards,\nBeal Computer"
    )
    msg["Subject"] = "Your Jobs are Done!"
    msg["From"] = USER
    msg["To"] = recipient

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(USER, PASS)
        s.send_message(msg)

file = Path("/Users/green/home/work/adar/software/SIMULATION_C_DRIVE/r270x_z_chunk.fastq")
email_user(file)
