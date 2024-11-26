from typing import Callable

from model.groups import Group
from model.rooms import Room
from model.subjects import Subject
from model.teachers import Teacher
from src.python.schedule.config import *

from src.python.schedule.schedule_state import *
from src.python.common.json.schedule_parser import map_json_to_schedule


def init_sch() -> SchState:


    # deprecated
    if default_init_enable:
        return get_sch_init_state(default_lecture_rooms,
                                  default_casual_rooms,
                                  default_teachers,
                                  default_subjects,
                                  default_lessons,
                                  default_casual_groups,
                                  default_lecture_groups,
                                  default_subjectGroup,
                                  default_subGroup,
                                  dummy
                                  )
    # deprecated
    elif test_init_enable:
        return get_sch_init_state(default_lecture_rooms,
                                  default_casual_rooms,
                                  default_teachers,
                                  default_subjects,
                                  default_lessons,
                                  default_casual_groups,
                                  default_lecture_groups,
                                  default_subjectGroup,
                                  default_subGroup,
                                  possible_test
                                  )

    elif test_via_json_init_enable:
        with open("resources/test_sch.json") as f:
            return map_json_to_schedule(f)

    raise Exception("no init state setting")


def possible_test(g, t, r, s, l):
    return t == g


def init_sch_by_models(teachers: dict[int, Teacher],
                       groups: dict[int, Group],
                       rooms: dict[int, Room],
                       subjects: dict[int, Subject]):
    return get_sch_init_state(teachers, groups, rooms, subjects, 30, dummy)
