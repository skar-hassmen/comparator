import os

from cfg_utils import *
from constants import list_instr
from StatisticDataBase import StatisticDataBase
import config_db

import idaapi
import idc
import idautils


def get_statistic_instructions(func) -> dict:
    instructions: list = [instr_ea for instr_ea in idautils.Heads(func.start_ea, func.end_ea)]
    statistic_instructions: dict = dict()
    count_bytes: int = 0

    for instr_name in list_instr:
        statistic_instructions[instr_name] = 0

    sum_id: int = 0
    for instr_ea in instructions:
        count_bytes += idc.get_item_size(instr_ea)
        instr_name: str = ida_ua.ua_mnem(instr_ea)

        if instr_name in list_instr:
            statistic_instructions[instr_name] += 1

        insn = idaapi.insn_t()
        if idaapi.decode_insn(insn, instr_ea) > 0:
            # сумма идентификаторов опкодов
            sum_id += insn.itype

    statistic_instructions["count_bytes"] = count_bytes
    statistic_instructions["sum_identify"] = sum_id

    return statistic_instructions


def serializer_instructions(statistic_instructions: dict) -> list[tuple]:
    list_instructions: list[tuple] = list()

    for key, value in statistic_instructions.items():
        if key != "count_bytes" and key != "sum_identify":
            list_instructions.append(tuple([key, value]))

    return list_instructions


def get_info_file() -> tuple:
    input_file: str = get_input_file_path().split("\\")[-1]
    tokens: list = input_file.split('.')

    return tokens[0], tokens[-1]


def entry_point():
    func_list: list = [func for func in idautils.Functions()]

    info_about_file: tuple = get_info_file()

    db = StatisticDataBase(config_db.host, config_db.user, config_db.password, config_db.db_name)
    db.start_connection()

    is_test_file: bool = False

    id_lib: int = db.insert_data_for_lib(info_about_file[0], info_about_file[1], 1, is_test_file)

    for func_entry in func_list:
        func = ida_funcs.get_func(func_entry)
        statistic_instructions: dict = get_statistic_instructions(func)

        if statistic_instructions["count_bytes"] <= 15:
            continue

        name_function = idc.get_func_name(func_entry)

        func_nodes: list = getNodes(func)
        func_edges: list = getEdges(func_nodes)

        graph: str = ""
        for edge in func_edges:
            graph += f'{edge};'

        id_function: int = db.insert_data_for_function(name_function, hex(func_entry),
                                                       statistic_instructions["count_bytes"],
                                                       statistic_instructions["sum_identify"], graph, id_lib)
        db.insert_data_for_instruction(serializer_instructions(statistic_instructions), id_function)

    db.close_connection()


if __name__ == '__main__':
    entry_point()

if "DO_EXIT" in os.environ:
    idc.qexit(1)
