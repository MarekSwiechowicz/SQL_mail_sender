import os
import csv
import smtplib
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

def getenv_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Brak wymaganej zmiennej środowiskowej {key}")
    return val

def getenv_int(key: str, default: int) -> int:
    val = os.getenv(key)
    return int(val) if val is not None else default

def getenv_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "t", "yes", "y"}

def getenv_list(key: str) -> list[str]:
    val = os.getenv(key, "")
    if not val.strip():
        return []
    return [x.strip() for x in val.split(",") if x.strip()]

# ========================
#   KONFIGURACJA BAZY
# ========================
DB_HOST = getenv_required("DB_HOST")
DB_PORT = getenv_int("DB_PORT", 5432)
DB_NAME = getenv_required("DB_NAME")
DB_USER = getenv_required("DB_USER")
DB_PASS = getenv_required("DB_PASS")

# ========================
#   ZAPYTANIE SQL
# ========================
SQL_QUERY = """
SELECT 
    TO_CHAR(rma_rma.created_at, 'YYYY-MM-DD HH24:MI') AS created_datetime,
    rma_rma.comment,
    authentication_user.email,
    allsafe_company.name AS company,
    rma_rma.qr_code,
    CONCAT('https://api.allsafe.3mk.pl/media/', rma_rma.product_image) AS product_image_url,
    CONCAT('https://api.allsafe.3mk.pl/media/', rma_rma.receipt_image) AS receipt_image_url
FROM rma_rma
JOIN authentication_user ON authentication_user.id = rma_rma.created_by_id
JOIN allsafe_company ON allsafe_company.id = authentication_user.company_id
WHERE 
    rma_rma.created_at >= date_trunc('month', CURRENT_DATE - interval '1 month')
    AND rma_rma.created_at < date_trunc('month', CURRENT_DATE)
    AND (
        allsafe_company.name IN (
            'eD system a.s.',
            'Titulo Glamoroso',
            'Available Gadget',
            'Nuovo mobile, UAB',
            'UAB Benieva'
        ) 
        OR allsafe_company.name = 'Josef KVAPIL a.s'
        OR allsafe_company.name = 'ED System'
    );
"""

# ========================
#   KONFIGURACJA MAILA
# ========================
SMTP_HOST = getenv_required("SMTP_HOST")
SMTP_PORT = getenv_int("SMTP_PORT", 587)
SMTP_USER = getenv_required("SMTP_USER")
SMTP_PASS = getenv_required("SMTP_PASS")
MAIL_FROM = getenv_required("MAIL_FROM")
MAIL_TO = getenv_list("MAIL_TO")
MAIL_SUBJECT = os.getenv("MAIL_SUBJECT", "Miesięczny Raport z Postgresa - CSV w załączniku")
USE_TLS = getenv_bool("USE_TLS", True)

CSV_FILENAME = os.getenv("CSV_FILENAME", "raport.csv")

def main():
    try:
        if not MAIL_TO:
            raise RuntimeError("Lista MAIL_TO jest pusta")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode="require"  # DigitalOcean PG zazwyczaj wymaga SSL
        )
        cursor = conn.cursor()

        cursor.execute(SQL_QUERY)
        rows = cursor.fetchall()

        headers = [
            "created_datetime", "comment", "email", "company",
            "qr_code", "product_image_url", "receipt_image_url"
        ]

        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)

        cursor.close()
        conn.close()

        msg = MIMEMultipart()
        msg["Subject"] = MAIL_SUBJECT
        msg["From"] = MAIL_FROM
        msg["To"] = ", ".join(MAIL_TO)

        body = (
            "Cześć,\n\n"
            "W załączniku przesyłam raport od pierwszego poprzedniego miesiąca do pierwszego tego miesiąca w formacie CSV.\n"
            "Pozdrawiam,\nMarekRaportBot"
        )
        msg.attach(MIMEText(body, "plain"))

        with open(CSV_FILENAME, "rb") as f:
            file_data = f.read()
            attachment = MIMEApplication(file_data, Name=CSV_FILENAME)
        attachment["Content-Disposition"] = f'attachment; filename="{CSV_FILENAME}"'
        msg.attach(attachment)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            if USE_TLS:
                s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())

        print("Mail wysłany pomyślnie, plik CSV w załączniku.")

    except Exception as e:
        print("Błąd:", e)

if __name__ == "__main__":
    main()
