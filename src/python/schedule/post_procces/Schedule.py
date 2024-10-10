import sys
from typing import Dict

from common.common import default_adder
from src.python.schedule.schedule_state import SchState

# Increase the recursion depth to 2000
sys.setrecursionlimit(20000)
i = 0
import logging

logging.basicConfig(level=logging.INFO, filename="", filemode="w")


class Slot:
    def __init__(self,
                 num,
                 raw_num,
                 groups: dict[int, int],
                 rooms: dict[int, int],
                 subjects: dict[int, int],
                 teachers: dict[int, int],
                 empty=False):
        self.num = num
        self.raw_num = raw_num
        self.groups = groups
        self.rooms = rooms
        self.subjects = subjects
        self.teachers = teachers
        self.is_empty = empty
        self.append_group = default_adder(groups, 0)
        self.append_rooms = default_adder(rooms, 0)
        self.append_teachers = default_adder(teachers, 0)
        self.append_subjects = default_adder(subjects, 0)
        self.state = []
        for g in groups.keys():
            for r in rooms.keys():
                for s in subjects.keys():
                    for t in teachers.keys():
                        self.state.append((g, r, s, t))

    def add_entity(self, g=-2, r=-2, s=-2, t=-2, value=1):
        # if g in self.groups:
        #     raise Exception

        if g == -2:
            for gn in self.groups.copy():
                self.add_entity(gn, r, s, t, value)
            return
        if r == -2:
            for rn in self.rooms.copy():
                self.add_entity(g, rn, s, t, value)
            return
        if s == -2:
            for sn in self.subjects.copy():
                self.add_entity(g, r, sn, t, value)
            return
        if t == -2:
            for tn in self.groups.copy():
                self.add_entity(g, r, s, tn, value)
            return

        self.append_group(g, value)
        self.append_rooms(r, value)
        self.append_subjects(s, value)
        self.append_teachers(t, value)
        self.state.append((g, r, s, t))
        self.is_empty = False

    def add_teacher(self, g, s, t):
        for entity in self.state:
            ge, re, se, te = entity
            if ge == g and se == s:
                self.state.remove((ge, re, se, te))
                self.state.append((ge, re, se, t))
                self.append_teachers(te, -1)
                self.append_teachers(t, 1)

    def conflicts(self) -> (str, int):
        msg = ""
        conflicts = 0
        for g in self.groups.keys():
            if g == -1:
                continue
            if self.groups[g] > 1:
                msg += "у группы: " + str(g + 1) + " проходит " + str(self.groups[g]) + " пар\n"
                conflicts += self.groups[g] - 1
        for r in self.rooms.keys():
            if r == -1:
                continue
            if self.rooms[r] > 1:
                msg += "в кабинете: " + str(r + 1) + " проходит " + str(self.rooms[r]) + " пар\n"
                conflicts += self.rooms[r] - 1
        for t in self.teachers.keys():
            if t == -1:
                continue
            if self.teachers[t] > 1:
                msg += "у преподавателя: " + str(t + 1) + " проходит " + str(self.teachers[t]) + " пар\n"
                conflicts += self.teachers[t] - 1
        return msg, conflicts


def empty_slot(num, raw_num):
    return Slot(num, raw_num, {}, {}, {}, {}, True)


class Day:
    @property
    def slots(self):
        return self._slots

    def all_slots(self):
        return self._slots.values()

    def __init__(self, slots: Dict[int, Slot]):
        self._slots = slots

    def add(self, slot: Slot, num: int):
        self.slots[num] = slot

    def __getitem__(self, item) -> Slot:
        return self.slots[item]

    def __setitem__(self, key: int, value: Slot):
        self.slots[key] = value

    @slots.setter
    def slots(self, value):
        self._slots = value


class Schedule:
    def __init__(self,
                 schedule_info,
                 sch_state: SchState,
                 days_num: int,
                 slots_num: int,
                 subjects_names: Dict[int, str],
                 groups_names: Dict[int, str],
                 rooms_names: Dict[int, str],
                 teacher_names: Dict[int, str]
                 ):
        self.sch_state = sch_state
        self.subjects_names = subjects_names
        self.groups_names = groups_names
        self.rooms_names = rooms_names
        self.teacher_names = teacher_names
        self.days = {}
        self.days_num = days_num
        self.slots_num = slots_num
        for d in range(days_num):
            self.days[d + 1] = Day({})
            for slot_num in range(slots_num):
                self.days[d + 1][slot_num + 1] = empty_slot(slot_num + 1, slot_num + (d * days_num))
        for k, v in schedule_info.items():
            if v == 0:
                continue
            r, s, l, g = k
            day_num, slot_num = self.get_day_and_slot(l)
            self[day_num][slot_num].add_entity(g, r, s, -1)

    def get_day_and_slot(self, l):
        return (l // self.slots_num) + 1, (l % self.slots_num) + 1

    def __getitem__(self, item: int) -> Day:
        return self.days[item]

    def alter_slots(self, g, s, t, l=-2):
        if l == -2:
            for day in self.days.values():
                for slot in day.slots.values():
                    slot.add_teacher(g, s, t)
            return
        day, slot = self.get_day_and_slot(l)
        self[day][slot].add_teacher(g, s, t)

    def print_sch(self):
        ans = {}
        errors = 0
        for day in range(self.days_num):
            for slot in range(self.slots_num):
                l = self[day + 1][slot + 1].raw_num
                ans[l] = "расписание на день " + str(day + 1) + " пара № " + str(slot + 1) + "\n"
                for entity in self[day + 1][slot + 1].state:
                    g, r, s, t = entity
                    ans[l] += self.subjects_names[s] + " проходит y грyппы " + self.groups_names[g] + " в кабинете " + \
                              self.rooms_names[r] + " у преподавателя " + self.teacher_names[t] + "\n"
                msg, conflicts = self[day + 1][slot + 1].conflicts()
                ans[l] += msg
                errors += conflicts

                print(ans[l])
        print("расписание содержит " + str(errors) + " конфликтов")
