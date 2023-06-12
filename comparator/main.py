from get_statistic.StatisticDataBase import StatisticDataBase
from get_statistic import config_db
from paths import ida_hunt, compiling_database_files, test_file, script1, script2
from analizator import analizator
from constants import fieldnames
from rw_csv import write_data_to_csv_file

from search import search_selen
from search import search_git

import os


def serializer_data_for_csv(rows: list) -> list:
    result: list = list()

    for row in rows:
        temp: dict = dict()
        for i in range(0, len(fieldnames)):
            temp[fieldnames[i]] = row[i + 1]
        result.append(temp)

    return result


def menu():
    print(
        '''
             <<< Menu Program >>>
            1. compiling database
            2. analize test file
            3. create database
            4. delete database
            5. write data result to csv
            6. search DuckDuckGo
            7. search GitHub
            8. exit program
        '''
    )


def choose_operation(db):
    state_database: bool = db.check_table("libs")

    while True:
        menu()

        try:
            command: int = int(input("Input command: "))
        except ValueError:
            print("[INFO] Wrong command!")
            continue

        if command == 1:
            if state_database is True:
                os.system(
                    f'python.exe {ida_hunt} --inputdir {compiling_database_files} --analyse --filter "filters\\names.py -a 64 -v" --scripts {script1}'
                )
            else:
                print("[INFO] database is already empty")
        elif command == 2:
            if state_database is True:
                os.system(
                    f'python.exe {ida_hunt} --inputdir {test_file} --analyse --filter "filters\\names.py -a 64 -v" --scripts {script2}'
                )

                if db.check_table("results") is True:
                    db.delete_results_table()

                db.create_results_table()
                analizator.start_analize(db)
            else:
                print("[INFO] database is already empty")
        elif command == 3:
            if state_database is False:
                db.create_tables()
                state_database = True
            else:
                print("[INFO] database already created")
        elif command == 4:
            if state_database is True:
                db.delete_tables()
                state_database = False
            else:
                print("[INFO] database is already empty")
        elif command == 5:
            if db.check_table("results") is True:
                rows: list = db.select_results()
                write_data_to_csv_file(path="result.csv", rows=serializer_data_for_csv(rows), fieldnames=fieldnames)
                print("[INFO] Data recording was successful")
            else:
                print("[INFO] Table of results is empty")
        elif command == 6:
            name_dll: str = input("Input name dll/lib (example func.dll or func): ")
            search_selen.entry_point(name_dll)
        elif command == 7:
            name_dll: str = input("Input name dll/lib (example func.dll or func): ")
            search_git.entry_point(name_dll)
        elif command == 8:
            return
        else:
            print("[INFO] Wrong command!")


def main():
    db = StatisticDataBase(config_db.host, config_db.user, config_db.password, config_db.db_name)
    db.start_connection()

    choose_operation(db)

    db.close_connection()


if __name__ == "__main__":
    main()
