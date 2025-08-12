import psycopg2
import csv
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ========================
#   KONFIGURACJA BAZY
# ========================
DB_HOST = "allsafe-db-do-user-7193655-0.c.db.ondigitalocean.com"  # Host bazy
DB_PORT = 25060                                                   # Port
DB_NAME = "prod_backend"                                          # Nazwa bazy
DB_USER = "marekswiechowicz"                                      # Użytkownik
DB_PASS = "weexee5AhFaesu"                                        # Hasło do bazy

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
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "marek.swiechowicz@3mk.pl"
SMTP_PASS = "gpsc uqel epxl wgwa"
MAIL_FROM = "marek.swiechowicz@3mk.pl"
MAIL_TO = [
    "iwona.spaleniak@3mk.pl",
    "filip.augustyniak@3mk.pl",
    "grzegorz.tomczyk@3mk.pl",
    "marek.swiechowicz@3mk.pl"
]
MAIL_SUBJECT = "Miesięczny Raport z Postgresa - CSV w załączniku"
USE_TLS = True

CSV_FILENAME = "raport.csv"

def main():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
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

        body = "Cześć,\n\nW załączniku przesyłam raport od pierwszego poprzedniego miesiąca do pierwszego tego miesiąca w formacie CSV. \nPozdrawiam,\nMarekRaportBot"
        msg.attach(MIMEText(body, "plain"))

        with open(CSV_FILENAME, "rb") as f:
            file_data = f.read()
            attachment = MIMEApplication(file_data, Name=CSV_FILENAME)
        attachment["Content-Disposition"] = f'attachment; filename="{CSV_FILENAME}"'
        msg.attach(attachment)

        if USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())

        # os.remove(CSV_FILENAME)

        print("Mail wysłany pomyślnie, plik CSV w załączniku.")

    except Exception as e:
        print("Błąd:", e)

if __name__ == "__main__":
    main()
