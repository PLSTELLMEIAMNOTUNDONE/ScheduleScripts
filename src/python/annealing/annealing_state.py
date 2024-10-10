from typing import Tuple

from src.python.schedule.post_procces.Schedule import Schedule
from src.python.schedule.schedule_state import SchState
from src.python.annealing.util import *
from copy import copy


def get_possible_pair_group_subject(sch_state: SchState):
    return list(filter(
        sch_state.sg_possible,
        list(sch_state.subject_group_map.keys())
    ))


def rand_relatable_pair_group_subject(sch_state: SchState):
    return choice(get_possible_pair_group_subject(sch_state))


class AnnealingState:
    def copy(self):
        return AnnealingState(self.state_map, self.unused_teachers, self.teachers_count)

    def __init__(self, state_map, unused_teachers, teachers_count):
        self.state_map = copy(state_map)
        self.unused_teachers = copy(unused_teachers)
        self.teachers_count = copy(teachers_count)

    def add(self, s, g, t):
        self.state_map[(s, g)] = t
        if self.teachers_count[t] == 0:
            self.unused_teachers.remove(t)
        self.teachers_count[t] += 1

    def change_schedule(self, schedule: Schedule):
        n = randrange(5) + 1
        fix = puff
        while n > 0:
            n -= 1
            if len(self.unused_teachers) == 0:
                us, ug = rand_relatable_pair_group_subject(schedule.sch_state)
                vs, vg = rand_relatable_pair_group_subject(schedule.sch_state)
                self.state_map[(us, ug)], self.state_map[(vs, vg)] = self.state_map[(vs, vg)], self.state_map[(us, ug)]
                fix = self.get_fix(ug, vg, us, vs, fix)
            else:
                us, ug = rand_relatable_pair_group_subject(schedule.sch_state)
                old_t = self.state_map[(us, ug)]
                new_t = self.unused_teachers.pop()
                self.state_map[(us, ug)] = new_t
                self.teachers_count[new_t] += 1
                self.teachers_count[old_t] -= 1
                if self.teachers_count[old_t] == 0:
                    self.unused_teachers.append(old_t)
                fix = self.get_fix(ug, ug, us, us, fix)
        return fix

    def get_fix(self, ug, vg, us, vs, pref_fix):
        def fix():
            self.state_map[(us, ug)], self.state_map[(vs, vg)] = self.state_map[(vs, vg)], self.state_map[(us, ug)]
            pref_fix()

        return fix

    def construct_schedule(self, schedule: Schedule):
        for k, v in self.state_map.items():
            s, g = k
            schedule.alter_slots(g, s, v)


def make_state(state: SchState):
    state_map = {}
    unused_teachers = [t for t in range(state.teachers)]
    teachers_count = [0 for _ in range(state.teachers)]
    return AnnealingState(state_map, unused_teachers, teachers_count)


def init_state(sch_state: SchState):
    state = make_state(sch_state)
    for g in range(sch_state.casual_groups):
        for s in range(sch_state.subjects):
            if sch_state.sg_possible((s, g)):
                new_t = randrange(sch_state.teachers)
                state.add(s, g, new_t)
    return state
