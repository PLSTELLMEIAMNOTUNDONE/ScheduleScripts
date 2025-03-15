from src.python.common.json.schedule_parser import map_spbu_data_to_schedule
from src.python.schedule.schedule_state import SchState


def init_sch() -> SchState:
    return map_spbu_data_to_schedule("src//tests//resources//test1")

def possible_test(g, t, r, s, l):
    return t == g
