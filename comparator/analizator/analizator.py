from networkx.algorithms import isomorphism

import time
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

    coff: int = 0

    # по одинаковому числу вершин и ребер
    if graph_db.number_of_nodes() == graph_test.number_of_nodes() and graph_db.number_of_edges() == graph_test.number_of_edges():
        coff += 1

    # по одинаковой структуре
    if set(graph_db.nodes()) == set(graph_test.nodes()) and set(graph_db.edges()) == set(graph_test.edges()):
        coff += 1

    # по графовому ядру
    gm = isomorphism.GraphMatcher(graph_db, graph_test)
    if gm.is_isomorphic():
        coff += 1

    if coff == 0:
        return 0.0

    print(coff)
    cost: int = nx.graph_edit_distance(graph_db, graph_test, timeout=0.5)
    similarity: float = 0.0

    if cost is None:
        similarity = 0
    elif cost == 0:
        similarity = 1
    else:
        if cost <= 50:
            similarity = 1 - (cost / 50)

    graph_db.clear()
    graph_test.clear()

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


def start_analize(db: object):
    start = time.time()

    list_libs: list = db.select_libs(is_test_file=False)
    test: list = db.select_libs(is_test_file=True)

    if len(test) > 0:
        test: tuple = test[0]
    else:
        print("[INFO] Test file was not found")
        return

    functions_test: list = db.select_functions([test[0]])

    libs: dict = dict()
    id_list: list = list()
    for lib in list_libs:
        libs[lib[0]] = {"name_lib": lib[1], "type_lib": lib[2], "version": lib[3]}
        id_list.append(lib[0])


    functions_db: list = db.select_functions(id_list)
    for function_test in functions_test:
        data_for_results: list[tuple] = list()
        for function_db in functions_db:
            similarity: float = compare_functions(function_test, function_db, db)

            if similarity >= 0.70:
                index_lib: int = function_db[6]
                data_for_results.append(
                    tuple(
                        [libs[index_lib]["name_lib"], libs[index_lib]["type_lib"], libs[index_lib]["version"], function_db[1], function_db[2], test[1], test[2], function_test[1],
                     function_test[2], similarity]
                    )
                )

        if(len(data_for_results)) > 0:
            db.insert_data_for_results(data_for_results)

    end = time.time()
    print(f"[INFO] The time of execution of analizator is: {round(end - start, 2)} sec.")
    print("[INFO] Analysis was successful")
