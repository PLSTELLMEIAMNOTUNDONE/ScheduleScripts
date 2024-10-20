from typing import Callable

from src.python.schedule.config import *

from src.python.schedule.schedule_state import *
from src.python.common.json.schedule_parser import map_json_to_schedule


def init_sch() -> SchState:
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


if __name__ == "__main__":
    init_sch()
