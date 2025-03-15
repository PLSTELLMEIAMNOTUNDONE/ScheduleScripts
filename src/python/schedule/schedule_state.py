from typing import Tuple, Callable

from model.groups import Group
from model.rooms import Room
from model.subjects import Subject
from model.teachers import Teacher


class SchState:
    def __init__(self,
                 teachers: dict[int, Teacher],
                 groups: dict[int, Group],
                 rooms: dict[int, Room],
                 subjects: dict[int, Subject],
                 lessons: int,
                 possible):
        self.teachers = teachers
        self.groups = groups
        self.rooms = rooms
        self.subjects = subjects
        self.lessons = lessons
        self.all_teachers = set(self.teachers.keys())
        self.all_groups = set(self.groups.keys())
        self.all_rooms = set(self.rooms.keys())
        self.all_subjects = set(self.subjects.keys())
        self.all_lessons = range(self.lessons)
        self.real_groups = []
        for group in groups.values():
            if group.is_real:
                self.real_groups.append(group.num)
        self.unity = {}
        self.united_groups = {}
        self.sub_groups = {}
        for g in groups.values():
            if not g.is_real:
                self.sub_groups[g.num] = g.sub_groups
        for g in groups.values():
            self.unity[g.num] = [g.num]
            self.united_groups[g.num] = [g.num]
        for pair in self.sub_groups.items():
            ug_i, ug = pair
            for g in ug:
                self.unity[g].append(ug_i)
                self.united_groups[ug_i].append(g)

        self.subject_group_map = {}
        for g in groups.values():
            for s in g.subjects:
                self.subject_group_map[(s.num, g.num)] = s.amount

        def default_possible(g, t, r, s, l):
            group = self.groups[g]
            subject = self.subjects[s]
            room = self.rooms[r]
            if not (s, g) in self.subject_group_map.keys():
                return False
            if room.capacity < group.volume:
                return False
            for requirement in subject.requirements:
                if not requirement in room.features:
                    return False
            return possible(g, t, r, s, l)

        self.origin_possible = possible
        self.possible = default_possible

    def __str__(self):
        return f"rooms: {self.rooms} \n groups: {self.groups} \n real_groups:  {self.real_groups}  \n sub_groups: {self.sub_groups} \n unity: {self.unity} \n teachers: {self.teachers} \n subjects: {self.subjects} \n subject_group_map: {self.subject_group_map}"

    def sg_possible(self, sg: Tuple[int, int]):
        return True


def dummy(g, t, r, s, l):
    return True


def get_sch_init_state(
        teachers: dict[int, Teacher],
        groups: dict[int, Group],
        rooms: dict[int, Room],
        subjects: dict[int, Subject],
        lessons: int,
        possible: Callable[[int, int, int, int, int], bool]) -> SchState:
    return SchState(teachers, groups, rooms, subjects, lessons, possible)
