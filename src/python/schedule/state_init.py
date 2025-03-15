from src.python.schedule.schedule_state import *

def init_sch_by_models(teachers: dict[int, Teacher],
                       groups: dict[int, Group],
                       rooms: dict[int, Room],
                       subjects: dict[int, Subject]):
    return get_sch_init_state(teachers, groups, rooms, subjects, 30, dummy)
