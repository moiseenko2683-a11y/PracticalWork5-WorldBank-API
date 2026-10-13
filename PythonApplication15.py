
import requests
import json
import csv


# Налаштування запиту
API_URL = (
    "https://api.worldbank.org/v2/country/all/"
    "indicator/NE.EXP.GNFS.ZS"
)

YEARS = [2015, 2019]
JSON_FILE = "exports_data.json"
CSV_FILE = "exports_data.csv"


def get_data():
    """Отримання даних зі Світового банку через API."""
    all_records = []
    page = 1

    try:
        while True:
            params = {
                "date": "2015:2019",
                "format": "json",
                "per_page": 20000,
                "page": page
            }

            response = requests.get(
                API_URL,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                print(
                    "Помилка HTTP-запиту:",
                    response.status_code
                )
                return None

            result = response.json()

            if not isinstance(result, list) or len(result) < 2:
                print("Помилка: отримано некоректні JSON-дані.")
                return None

            metadata = result[0]
            records = result[1] or []

            all_records.extend(records)

            total_pages = int(metadata.get("pages", 1))

            if page >= total_pages:
                break

            page += 1

        # Залишаємо тільки 2015 і 2019 роки
        filtered_records = []

        for record in all_records:
            if record.get("date") not in ["2015", "2019"]:
                continue

            # Виключаємо агреговані регіони та групи країн
            country = record.get("country", {})
            region = country.get("region", {})

            if region.get("id") == "NA":
                continue

            filtered_records.append({
                "country": country.get("value", ""),
                "country_code": record.get(
                    "countryiso3code", ""
                ),
                "year": int(record["date"]),
                "indicator": record.get(
                    "indicator", {}
                ).get("value", ""),
                "value": record.get("value")
            })

        print("HTTP-запит виконано успішно.")
        print("Кількість отриманих записів:",
              len(filtered_records))

        return filtered_records

    except requests.exceptions.RequestException as error:
        print("Помилка під час HTTP-запиту:", error)
        return None
    except (ValueError, TypeError, KeyError) as error:
        print("Помилка оброблення даних:", error)
        return None


def save_json(data):
    """Збереження даних у форматі JSON."""
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(f"JSON-файл збережено: {JSON_FILE}")
        return True

    except OSError as error:
        print("Помилка запису JSON-файлу:", error)
        return False


def save_csv(data):
    """Перетворення даних і збереження у форматі CSV."""
    try:
        with open(
            CSV_FILE, "w", newline="", encoding="utf-8-sig"
        ) as file:
            fieldnames = [
                "country",
                "country_code",
                "year",
                "indicator",
                "value"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                delimiter=";"
            )

            writer.writeheader()
            writer.writerows(data)

        print(f"CSV-файл збережено: {CSV_FILE}")
        return True

    except OSError as error:
        print("Помилка запису CSV-файлу:", error)
        return False


def display_file(filename):
    """Виведення вмісту файлу на екран."""
    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            print(f"\n{'=' * 60}")
            print(f"ВМІСТ ФАЙЛУ {filename}")
            print("=" * 60)
            print(file.read())

    except OSError as error:
        print(f"Помилка читання файлу {filename}:", error)


def main():
    """Головна функція програми."""
    print("ПРАКТИЧНА РОБОТА № 5")
    print("Отримання та оброблення даних із вебджерел")
    print("Показник: Exports of goods and services (% of GDP)")
    print("Роки: 2015 і 2019\n")

    data = get_data()

    if data is None:
        print("Не вдалося отримати дані.")
        return

    if not data:
        print("Дані за вказані роки відсутні.")
        return

    json_saved = save_json(data)
    csv_saved = save_csv(data)

    if json_saved:
        display_file(JSON_FILE)

    if csv_saved:
        display_file(CSV_FILE)


if __name__ == "__main__":
    main()

