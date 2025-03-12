import psycopg2
import smtplib
from email.mime.text import MIMEText

# ========================
#   KONFIGURACJA BAZY
# ========================
DB_HOST = "allsafe-db-do-user-7193655-0.c.db.ondigitalocean.com"  # Host bazy
DB_PORT = 25060                                                   # Port
DB_NAME = "prod_backend"                                          # Nazwa bazy
DB_USER = "marekswiechowicz"                                      # Użytkownik
DB_PASS = "weexee5AhFaesu"                                # Hasło do bazy

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
SMTP_HOST = "smtp.gmail.com"                              # Serwer SMTP (np. Gmail)
SMTP_PORT = 587                                           # Port Gmail (STARTTLS)
SMTP_USER = "marek.swiechowicz@3mk.pl"                    # Twój adres Gmail
SMTP_PASS = "M@@rek111"              # Hasło aplikacji Gmail (app password)
MAIL_FROM = "marek.swiechowicz@3mk.pl"                    # Najlepiej taki sam adres co SMTP_USER
MAIL_TO = "marek.swiechowicz@3mk.pl"                           # Możesz wpisać jeden lub wiele adresów
MAIL_SUBJECT = "Miesięczny Raport z Postgresa"
USE_TLS = True  # Gmail zwykle wymaga TLS (starttls)


def main():
    try:
        # 1) Połączenie z bazą
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()

        # 2) Wykonaj zapytanie
        cursor.execute(SQL_QUERY)
        rows = cursor.fetchall()

        # 3) Format wyników do tekstu (CSV w wersji minimalnej)
        results_as_text = ""
        for row in rows:
            results_as_text += ";".join(str(x) for x in row) + "\n"

        cursor.close()
        conn.close()

        # 4) Przygotuj maila
        msg = MIMEText(results_as_text)
        msg["Subject"] = MAIL_SUBJECT
        msg["From"] = MAIL_FROM
        msg["To"] = MAIL_TO

        # 5) Wyślij maila
        if USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())

        print("Mail wysłany pomyślnie.")

    except Exception as e:
        print("Błąd:", e)


if __name__ == "__main__":
    main()
