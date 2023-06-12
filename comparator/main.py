from get_statistic.StatisticDataBase import StatisticDataBase
from get_statistic import config_db
from paths import ida_hunt, compiling_database_files, test_file, script1, script2
from analizator import analizator

import os


def menu():
    print(
        '''
             <<< Menu Program >>>
            1. compiling database
            2. analize test file
            3. create database
            4. delete database
            5. exit program
        '''
    )


def choose_operation(db):
    state_database: bool = db.check_table()

    while True:
        menu()
        command: int = int(input("Input command: "))
        if command == 1:
            if state_database is True:
                os.system(
                    f'python.exe {ida_hunt} --inputdir {compiling_database_files} --analyse --filter "filters\\names.py -a 32 -v" --scripts {script1}'
                )
            else:
                print("[INFO] Database is already empty")
        elif command == 2:
            if state_database is True:
                os.system(
                    f'python.exe {ida_hunt} --inputdir {test_file} --analyse --filter "filters\\names.py -a 32 -v" --scripts {script2}'
                )
                analizator.start_analize(db)
            else:
                print("[INFO] Database is already empty")
        elif command == 3:
            if state_database is False:
                db.create_tables()
                state_database = True
            else:
                print("[INFO] Database already created")
        elif command == 4:
            if state_database is True:
                db.delete_tables()
                state_database = False
            else:
                print("[INFO] Database is already empty")
        elif command == 5:
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
