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
SMTP_PASS = "cidq pdci lrsj hryu"              # Hasło aplikacji Gmail (app password)
MAIL_FROM = "marek.swiechowicz@3mk.pl"                    # Najlepiej ten sam adres co SMTP_USER
MAIL_TO = "filip.augustyniak@3mk.pl"                           # Możesz wpisać jeden lub wiele adresów
MAIL_SUBJECT = "Miesięczny Raport z Postgresa - CSV w załączniku"
USE_TLS = True  # Gmail zwykle wymaga TLS (starttls)

# Nazwa pliku CSV do zapisania i wysłania
CSV_FILENAME = "raport.csv"

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

        # 3) Zapisz wyniki do pliku CSV
        # Zdefiniuj nagłówki, jeśli chcesz (lub pobierz z cursor.description)
        headers = [
            "created_datetime", "comment", "email", "company",
            "qr_code", "product_image_url", "receipt_image_url"
        ]

        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            # Zapisz nagłówki
            writer.writerow(headers)
            # Zapisz dane
            for row in rows:
                writer.writerow(row)

        cursor.close()
        conn.close()

        # 4) Przygotuj maila (multipart, żeby dodać załącznik)
        msg = MIMEMultipart()
        msg["Subject"] = MAIL_SUBJECT
        msg["From"] = MAIL_FROM
        msg["To"] = MAIL_TO

        # Wiadomość tekstowa w treści maila
        body = "Cześć,\n\nW załączniku przesyłam raport od pierwszego do pierwszego tego miesiąca w formacie CSV. \nPozdrawiam,\nMarekRaportBot"
        msg.attach(MIMEText(body, "plain"))

        # 5) Dodaj załącznik (plik CSV)
        with open(CSV_FILENAME, "rb") as f:
            file_data = f.read()
            # Utwórz obiekt MIMEApplication do załącznika
            attachment = MIMEApplication(file_data, Name=CSV_FILENAME)
        # Ustaw nagłówki załącznika
        attachment["Content-Disposition"] = f'attachment; filename="{CSV_FILENAME}"'
        msg.attach(attachment)

        # 6) Wyślij maila
        if USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())

        # Ewentualne posprzątanie pliku CSV (jeśli nie chcesz go przechowywać)
        # os.remove(CSV_FILENAME)

        print("Mail wysłany pomyślnie, plik CSV w załączniku.")

    except Exception as e:
        print("Błąd:", e)

if __name__ == "__main__":
    main()
