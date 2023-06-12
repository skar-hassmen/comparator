import psycopg2


class StatisticDataBase:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StatisticDataBase, cls).__new__(cls)
        return cls.instance

    def __init__(self, host: str, user: str, password: str, db_name: str):
        self.__connection = None
        self.__host = host
        self.__user = user
        self.__password = password
        self.__db_name = db_name

    def start_connection(self):
        try:
            self.__connection = psycopg2.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__db_name
            )
            print("[DATABASE] PostgreSQL connection open")
        except Exception as ex:
            print("[DATABASE] Error connection by PostgreSQL", ex)

    def close_connection(self):
        if self.__connection is not None:
            self.__connection.close()
            print("[DATABASE] PostgreSQL connection closed")

    def check_table(self, name_table: str) -> bool:
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT EXISTS (
                        SELECT 1
                        FROM pg_tables
                        WHERE tablename = %s
                    );
                    ''',
                    (name_table,)
                )
                self.__connection.commit()
                return bool(cursor.fetchall()[0][0])

    def create_tables(self):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    CREATE TABLE libs (
                        id serial PRIMARY KEY,
                        name_lib varchar(255) NOT NULL,
                        type_lib varchar(3) NOT NULL,
                        version int NOT NULL,
                        is_test_file boolean NOT NULL
                    );
                    
                    CREATE TABLE functions (
                        id serial PRIMARY KEY,
                        name_function varchar(255) NOT NULL,
                        offset_function varchar(255) NOT NULL,
                        count_bytes int NOT NULL,
                        sum_identify int NOT NULL,
                        graph text NOT NULL, 
                        fk_functions_libs int REFERENCES libs(id)
                    );
                    
                    CREATE TABLE instructions (
                        id serial PRIMARY KEY,
                        name_instruction varchar(255) NOT NULL,
                        count_instruction int NOT NULL,
                        fk_instructions_functions int REFERENCES functions(id)
                    );
                    '''
                )
                self.__connection.commit()
                print("[DATABASE] Tables (libs, functions, instructions) were created")

    def create_results_table(self):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    CREATE TABLE results (
                        id serial PRIMARY KEY,
                        lib_name varchar(255) NOT NULL,
                        lib_type varchar(3) NOT NULL,
                        lib_version int NOT NULL,
                        lib_function_name varchar(255) NOT NULL,
                        lib_function_offset varchar(255) NOT NULL,
                        test_name varchar(255) NOT NULL,
                        test_type varchar(3) NOT NULL,
                        test_function_name varchar(255) NOT NULL,
                        test_function_offset varchar(255) NOT NULL,
                        similarity float NOT NULL
                    );
                    '''
                )
                self.__connection.commit()
                print("[DATABASE] Table (results) was created")

    def insert_data_for_lib(self, name_lib: str, type_lib: str, version: int, is_test_file: bool) -> int:
        id_created_record: int = -1
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO libs (name_lib, type_lib, version, is_test_file) 
                    VALUES (%s, %s, %s, %s)
                    
                    RETURNING id
                    ''',
                    (name_lib, type_lib, version, is_test_file)
                )
                self.__connection.commit()
                id_created_record = cursor.fetchall()[0][0]

        return id_created_record

    def insert_data_for_function(self, name_function: str, offset_function: str, count_bytes: int, sum_identify: int, graph: str, fk_functions_libs: int) -> int:
        id_created_record: int = -1
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO functions (name_function, offset_function, count_bytes, sum_identify, graph, fk_functions_libs) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    
                    RETURNING id
                    ''',
                    (name_function, offset_function, count_bytes, sum_identify, graph, fk_functions_libs)
                )
                self.__connection.commit()
                id_created_record = cursor.fetchall()[0][0]

        return id_created_record

    def insert_data_for_instruction(self, list_instructions: list[tuple], fk_instructions_functions: int):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                for elem_instruction in list_instructions:
                    cursor.execute(
                        '''
                        INSERT INTO instructions (name_instruction, count_instruction, fk_instructions_functions) 
                        VALUES (%s, %s, %s)

                        RETURNING id
                        ''',
                        (elem_instruction[0], elem_instruction[1], fk_instructions_functions)
                    )
                self.__connection.commit()

    def insert_data_for_results(self, list_result: list[tuple]):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.executemany(
                    '''
                    INSERT INTO results (
                        lib_name, lib_type, lib_version, 
                        lib_function_name, lib_function_offset, test_name,
                        test_type, test_function_name, test_function_offset, 
                        similarity
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                    RETURNING id
                    ''',
                    list_result
                )
                self.__connection.commit()

    def select_libs(self, is_test_file: bool) -> list:
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT * FROM libs WHERE libs.is_test_file=%s
                    ''',
                    (str(is_test_file),)
                )

                self.__connection.commit()
                return cursor.fetchall()

    def select_functions(self, id_list: list):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT * FROM functions WHERE functions.fk_functions_libs IN %s;
                    ''',
                    (tuple(id_list),)
                )

                self.__connection.commit()
                return cursor.fetchall()

    def select_instructions(self, id_function: int):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT * FROM instructions WHERE instructions.fk_instructions_functions=%s
                    ''',
                    (str(id_function),)
                )

                self.__connection.commit()
                return cursor.fetchall()

    def select_results(self):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT * FROM results; 
                    '''
                )
                self.__connection.commit()
                return cursor.fetchall()

    def delete_tables(self):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    DROP TABLE libs CASCADE;
                    DROP TABLE functions CASCADE;
                    DROP TABLE instructions CASCADE;
                    '''
                )
                self.__connection.commit()
                print("[DATABASE] Tables (libs, functions, instructions) were deleted")

    def delete_results_table(self):
        if self.__connection is not None:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    '''
                    DROP TABLE results;
                    '''
                )
                self.__connection.commit()
                print("[DATABASE] Table (results) was deleted")
