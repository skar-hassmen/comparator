import csv


def write_data_to_csv_file(path: str, rows: list, fieldnames: list):
    with open(path, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_data_from_csv_file(path: str) -> list:
    rows: list = list()
    with open("db.csv", mode="r", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        for row in reader:
            rows.append(row)

    return rows
