# 📊 Miesięczny Raport z Postgresa (CSV na maila)

Ten skrypt w Pythonie generuje miesięczny raport RMA z bazy danych PostgreSQL, zapisuje go w pliku CSV, a następnie wysyła jako załącznik na zdefiniowane adresy e-mail.

---

## 🔧 Wymagania

- Python 3.x
- Biblioteki:
  - `psycopg2`
  - `smtplib` _(standardowa biblioteka Pythona)_
  - `email` _(standardowa biblioteka Pythona)_
  - `csv`
  - `os`

Instalacja wymaganej biblioteki:

```bash
pip install psycopg2
```

---

## ⚙️ Konfiguracja

### 1. Dane dostępowe do bazy danych

Uzupełnij dane w sekcji:

```python
DB_HOST = "..."
DB_PORT = ...
DB_NAME = "..."
DB_USER = "..."
DB_PASS = "..."
```

### 2. Zapytanie SQL

Zapytanie pobiera dane z ostatniego miesiąca (od pierwszego do pierwszego). Dostosuj je, jeśli potrzebujesz innych danych.

### 3. Ustawienia mailowe

Ustaw dane SMTP i odbiorców:

```python
SMTP_USER = "twoj_email@gmail.com"
SMTP_PASS = "twoje_haslo_aplikacji"
MAIL_TO = ["adres1@example.com", "adres2@example.com"]
```

> ℹ️ Jeśli używasz Gmaila, utwórz **hasło aplikacji** (wymagana aktywna weryfikacja dwuetapowa).

---

## 📁 Wynik działania

Skrypt tworzy plik `raport.csv` z danymi, a następnie wysyła go jako załącznik w wiadomości e-mail.

Przykładowa wiadomość e-mail:

- **Temat:** Miesięczny Raport z Postgresa - CSV w załączniku
- **Treść:**

  ```
  Cześć,

  W załączniku przesyłam raport od pierwszego do pierwszego tego miesiąca w formacie CSV.

  Pozdrawiam,
  MarekRaportBot
  ```

---

## ▶️ Jak uruchomić

Po skonfigurowaniu uruchom skrypt:

```bash
python raport.py
```

---

## 📌 Uwagi końcowe

- Aby usunąć plik CSV po wysyłce, odkomentuj linię:

  ```python
  # os.remove(CSV_FILENAME)
  ```

- Jeśli napotkasz błędy związane z połączeniem SMTP lub bazą danych:
  - sprawdź połączenie z internetem,
  - zweryfikuj poprawność danych logowania.

---

## ✅ Co robi ten skrypt?

1. Łączy się z bazą PostgreSQL.
2. Wykonuje zapytanie SQL.
3. Zapisuje dane do `raport.csv`.
4. Przygotowuje wiadomość e-mail.
5. Wysyła wiadomość z załącznikiem CSV.
6. (Opcjonalnie) usuwa plik po wysyłce.

---

## 📂 Struktura CSV

Plik `raport.csv` zawiera kolumny:

- `created_datetime`
- `comment`
- `email`
- `company`
- `qr_code`
- `product_image_url`
- `receipt_image_url`

---

Gotowe! 🎉 Skrypt działa w pełni automatycznie i może być uruchamiany np. przez CRON.
