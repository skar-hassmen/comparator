from analizator.constants import fieldnames
from analizator.rw_csv import write_data_to_csv_file

import networkx as nx


def compare_numbers(number1: int, number2: int) -> float:
    if number1 == number2:
        return 1.0
    elif number1 > number2:
        return number2 / number1
    else:
        return number1 / number2


def compare_count_bytes(count_bytes_db: int, count_bytes_test: int) -> float:
    return compare_numbers(count_bytes_db, count_bytes_test)


def compare_sum_identify(sum_identify_db: int, sum_identify_test: int) -> float:
    return compare_numbers(sum_identify_db, sum_identify_test)


def compare_instructions(function_id_db: int, function_id_test: int, db: object) -> float:
    sum_k: float = 0.0

    instructions_db: list = db.select_instructions(function_id_db)
    instructions_test: list = db.select_instructions(function_id_test)

    count_instruction: int = len(instructions_db)

    for i in range(0, count_instruction):
        sum_k += compare_numbers(instructions_db[i][2], instructions_test[i][2])

    return sum_k / count_instruction


def create_graph(str_graph: str):
    graph = nx.Graph()

    tokens: list = str_graph.split(";")

    for i in range(0, len(tokens) - 1):
        temp: list = tokens[i].split("->")
        graph.add_edge(int(temp[0]), int(temp[1]))

    return graph


def compare_graphs(str_graph_db: str, str_graph_test) -> float:
    graph_db = create_graph(str_graph_db)
    graph_test = create_graph(str_graph_test)

    cost: int = nx.graph_edit_distance(graph_db, graph_test, timeout=0.5)
    similarity: float = 0.0

    if cost is None:
        similarity = 0
    elif cost == 0:
        similarity = 1
    elif cost < 10:
        similarity = 0.8
    elif cost < 30:
        similarity = 0.6
    elif cost < 50:
        similarity = 0.4
    elif cost < 80:
        similarity = 0.2

    graph_db.clear()
    graph_db.clear()

    return similarity


def compare_functions(function_db: tuple, function_test: tuple, db: object):
    if function_db[5] == function_test[5]:
        return 1.0

    k1: float = compare_count_bytes(function_db[3], function_test[3])

    if k1 < 0.5:
        return 0.0

    k2: float = compare_sum_identify(function_db[4], function_test[4])

    if k2 < 0.6:
        return 0.0

    k3: float = compare_instructions(function_db[0], function_test[0], db)

    if k3 < 0.85:
        return 0.0

    k4: float = compare_graphs(function_db[5], function_test[5])

    return (k1 + k2 + k3 + k4) / 4


def serializer_data_for_table_csv(data):
    result: dict = dict()

    for i in range(0, len(fieldnames)):
        result[fieldnames[i]] = data[i]

    return result


def start_analize(db: object):
    list_libs: list = db.select_libs(is_test_file=False)
    test: tuple = list_libs[0]
    functions_test: list = db.select_functions(test[0])

    rows: list = list()

    for lib in list_libs:
        functions_db = db.select_functions(lib[0])
        for function_test in functions_test:
            for function_db in functions_db:
                similarity: float = compare_functions(function_test, function_db, db)
                rows.append(
                    serializer_data_for_table_csv([lib[1], lib[2], lib[3], function_db[1], function_db[2], test[1], test[2], functions_test[1], function_db[2], similarity])
                )

    if len(rows) != 0:
        write_data_to_csv_file(path="result.csv", rows=rows, fieldnames=fieldnames)
