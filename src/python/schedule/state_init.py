from src.python.schedule.config import *

from src.python.schedule.schedule_state import *


def get_sch_init_state(
        lecture_rooms: int,
        casual_rooms: int,
        teachers: int,
        subjects: int,
        lessons: int,
        casual_groups: int,
        lecture_groups: int,
        subject_to_group: list[list[int]],
        sub_groups: dict[int, list[int]]) -> SchState:
    return SchState(lecture_rooms, casual_rooms, teachers, subjects, lessons, casual_groups, lecture_groups,
                    subject_to_group, sub_groups)


def init_state():
    if default_init_enable:
        return get_sch_init_state(default_lecture_rooms, default_casual_rooms, default_teachers, default_subjects,
                                  default_lessons,
                                  default_casual_groups, default_lecture_groups, default_subjectGroup, default_subGroup)
    raise Exception("no init state setting")


if __name__ == "__main__":
    init_state()
