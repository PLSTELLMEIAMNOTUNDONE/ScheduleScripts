from typing import Callable

from model.NameAware import NameAware
from model.groups import Group
from model.rooms import Room
from model.subjects import Subject
from model.teachers import Teacher
from schedule.schedule_state import get_sch_init_state, SchState


def add_with_id(items: dict, names: dict):
    item_id = -1

    def add(value: NameAware):
        if not value.name in names.keys():
            nonlocal item_id
            item_id += 1
            value.set_id(item_id)
            items[item_id] = value
            names[value.name] = item_id
            return item_id
        else:
            return names[value.name]

    return add


class ScheduleAggregator:
    def __init__(self, lessons: int):
        self.teachers = {}
        self.subjects = {}
        self.groups = {}
        self.rooms = {}
        self.t_id_by_name = {}
        self.s_id_by_name = {}
        self.g_id_by_name = {}
        self.r_id_by_name = {}
        self.add_teacher = add_with_id(self.teachers, self.t_id_by_name)
        self.add_subject = add_with_id(self.subjects, self.s_id_by_name)
        self.add_group = add_with_id(self.groups, self.g_id_by_name)
        self.add_room = add_with_id(self.rooms, self.r_id_by_name)
        self.lessons = lessons

    def write_teacher(self, name: str):
        self.add_teacher(Teacher(name))

    def write_group(self, name: str, is_real: bool, volume: int, sub_groups: list[int] = None):
        self.add_group(Group(name, is_real, volume, [], sub_groups))

    def write_room(self, name: str, capacity: int, features: list[str]):
        self.add_room(Room(name, capacity, features))

    def write_subject(self, name: str, amount: int, requirements: list[str]):
        self.add_subject(Subject(name, amount, requirements))

    def link_group_subject(self, subject: str, group: str):
        g = self.g_id_by_name[group]
        s = self.s_id_by_name[subject]
        self.groups[g].subjects.add(self.subjects[s])

    def finish_aggregation(self, possible: Callable[[int, int, int, int, int], bool]) -> SchState:
        return get_sch_init_state(
            self.teachers,
            self.groups,
            self.rooms,
            self.subjects,
            self.lessons,
            possible
        )
