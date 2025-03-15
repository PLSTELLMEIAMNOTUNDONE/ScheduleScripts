import sys
from typing import Dict, Callable

from model.NameAware import NameAware
from src.python.common.common import with_cache
from src.python.common.common import default_adder
from src.python.common.records.recorder import recorder
from src.python.schedule.schedule_state import SchState

# Increase the recursion depth to 2000
sys.setrecursionlimit(20000)
i = 0
recorder = recorder("Schedule", True)


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
        self.get_for_group = with_cache(self.get_for_group_imp)
        self.get_for_rooms = with_cache(self.get_for_room_imp)
        self.get_for_teachers = with_cache(self.get_for_teacher_imp)
        self.get_for_subjects = with_cache(self.get_for_subject_imp)
        self.state = []
        for g in groups.keys():
            for r in rooms.keys():
                for s in subjects.keys():
                    for t in teachers.keys():
                        self.state.append((g, r, s, t))

    # unstable
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

    def get_for_group_imp(self, g: int):
        return list(filter(lambda x: x[0] == g, self.state))

    def get_for_room_imp(self, r: int):
        return list(filter(lambda x: x[1] == r, self.state))

    def get_for_subject_imp(self, s: int):
        return list(filter(lambda x: x[2] == s, self.state))

    def get_for_teacher_imp(self, t: int):
        return list(filter(lambda x: x[3] == t, self.state))


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


class MutableSchedule:
    def __init__(self,
                 days_num: int,
                 slots_num: int,
                 schedule_info=None
                 ):
        self.days = {}
        self.days_num = days_num
        self.slots_num = slots_num
        for d in range(days_num):
            self.days[d + 1] = Day({})
            for slot_num in range(slots_num):
                self.days[d + 1][slot_num + 1] = empty_slot(slot_num + 1, slot_num + (d * days_num))

        self.actions_by_name = {
            "group": self.get_schedule_for_group,
            "room": self.get_schedule_for_room,
            "teacher": self.get_schedule_for_teacher,
            "subject": self.get_schedule_for_subject
        }

        if schedule_info is not None:
            self.init_by_map(schedule_info)

    def init_by_map(self, schedule_info):
        for k, v in schedule_info.items():
            if v == 0:
                continue
            r, s, l, g, t = k
            day_num, slot_num = self.get_day_and_slot(l)
            self[day_num][slot_num].add_entity(g, r, s, t)

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

    def get_schedule_for_group(self, g: int):
        ans = {}
        for day in self.days.values():
            for slot in day.slots.values():
                entity = slot.get_for_group(g)
                if len(entity) > 0:
                    ans[slot.raw_num] = entity
        return ans

    def get_schedule_for_room(self, r: int):
        ans = {}
        for day in self.days.values():
            for slot in day.slots.values():
                entity = slot.get_for_rooms(r)
                if len(entity) > 0:
                    ans[slot.raw_num] = entity
        return ans

    def get_schedule_for_teacher(self, t: int):
        ans = {}
        for day in self.days.values():
            for slot in day.slots.values():
                entity = slot.get_for_teachers(t)
                if len(entity) > 0:
                    ans[slot.raw_num] = entity
        return ans

    def get_schedule_for_subject(self, s: int):
        ans = {}
        for day in self.days.values():
            for slot in day.slots.values():
                entity = slot.get_for_subjects(s)
                if len(entity) > 0:
                    ans[slot.raw_num] = entity
        return ans


class Schedule(MutableSchedule):
    def __init__(self, schedule_info, sch_state: SchState, days_num: int, slots_num: int):
        super().__init__(days_num, slots_num, schedule_info)
        self.sch_state = sch_state

    def readable_schedule(self) -> str:
        ans = {}
        ans_str = ""
        delimiter = "\n---\n|\n|\n ---\n"
        errors = 0
        for day in range(self.days_num):
            for slot in range(self.slots_num):
                l = self[day + 1][slot + 1].raw_num
                ans[l] = delimiter + "расписание на день " + str(day + 1) + " пара № " + str(slot + 1) + "\n"
                for entity in self[day + 1][slot + 1].state:
                    g, r, s, t = entity
                    ans[l] += self.sch_state.subjects[s].name + " проходит y грyппы " + self.sch_state.groups[
                        g].name + " в кабинете " + \
                              self.sch_state.rooms[r].name + " у преподавателя " + self.sch_state.teachers[
                                  t].name + "\n"
                ans[l] += delimiter + " найденные конфликты "
                msg, conflicts = self[day + 1][slot + 1].conflicts()
                ans[l] += msg
                errors += conflicts

                ans_str += ans[l]
        ans_str += ("расписание содержит " + str(errors) + " конфликтов")
        return ans_str

    # g, r, s, t - tuple order
    def _temp_for_windows(self, obj_dict: dict[int, NameAware], index: int, exclude: Callable[[int], bool]=lambda _: True):
        ans = 0
        last_in_day = {}
        for d in self.days.keys():
            last_in_day[d] = {}
            for obj in obj_dict.keys():
                last_in_day[d][obj] = -1

        for d, day in self.days.items():
            for p, slot in day.slots.items():
                for entity in slot.state:
                    obj = entity[index]
                    # TODO normal way to exclude stuff of cache idk
                    if exclude(obj):
                        continue
                    if last_in_day[d][obj] != -1 and last_in_day[d][obj] < p - 1:
                        ans += 1
                        recorder.record("Окна у" +
                                        obj_dict[obj].name +
                                        ", в день " + str(d) +
                                        ", пара номер " +
                                        str(p) + ", номер предыдущей пары " +
                                        str(last_in_day[d][obj]))
                    last_in_day[d][obj] = p
        return ans

    def _temp_for_conflict(self, obj_dict: dict[int, NameAware], index: int):
        ans = 0
        obj_in_timeslot: dict[int, set[int]] = {}
        for d, day in self.days.items():
            for p, slot in day.slots.items():
                for entity in slot.state:
                    timeslot = slot.raw_num
                    obj = entity[index]
                    if not timeslot in obj_in_timeslot.keys():
                        obj_in_timeslot[timeslot] = set([])
                    if obj in obj_in_timeslot[timeslot]:
                        ans += 1
                        if ans > 1:
                            recorder.record("Конфликты в слот " + str(timeslot) + " у объекта + " + str(obj), True)
                    obj_in_timeslot[timeslot].add(obj)

        return ans

    def conflicts_in_teachers(self):
        return self._temp_for_conflict(self.sch_state.teachers, 3)

    def conflicts_in_rooms(self):
        return self._temp_for_conflict(self.sch_state.rooms, 1)

    def conflicts_in_groups(self):
        return self._temp_for_conflict(self.sch_state.groups, 0)

    def windows_for_teachers(self):
        recorder.record("Найденные окна у учителей")
        return self._temp_for_windows(self.sch_state.teachers, 3)

    def windows_for_groups(self):
        recorder.record("Найденные окна у групп")
        return self._temp_for_windows(self.sch_state.groups, 0, lambda g: self.sch_state.groups[g].is_real)

    def size(self):
        ans = 0
        for d, day in self.days.items():
            for p, slot in day.slots.items():
                for entity in slot.state:
                    ans += 1
        return ans

    def make_record(self):
        recorder.record(self.readable_schedule())
