from copy import copy
from random import choice, randrange

from numpy.ma.mrecords import addfield

from model.Event import Event
from src.python.annealing.util import *
from src.python.schedule.post_procces.Schedule import Schedule
from src.python.schedule.schedule_state import SchState


def get_possible_pair_group_subject(schedule: Schedule):
    sch_state = schedule.sch_state
    return list(filter(
        sch_state.sg_possible,
        list(sch_state.subject_group_map.keys())
    ))


def rand_relatable_pair_group_subject(schedule: Schedule):
    return choice(get_possible_pair_group_subject(schedule))


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
                us, ug = rand_relatable_pair_group_subject(schedule)
                vs, vg = rand_relatable_pair_group_subject(schedule)
                self.state_map[(us, ug)], self.state_map[(vs, vg)] = self.state_map[(vs, vg)], self.state_map[(us, ug)]
                fix = self.get_fix(ug, vg, us, vs, fix)
            else:
                us, ug = rand_relatable_pair_group_subject(schedule)
                old_t = self.state_map[(us, ug)]
                new_t = self.unused_teachers.pop()
                self.state_map[(us, ug)] = new_t
                self.teachers_count[new_t] += 1
                self.teachers_count[old_t] -= 1
                if self.teachers_count[old_t] == 0:
                    self.unused_teachers.add(old_t)
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
    unused_teachers = state.all_teachers
    teachers_count = {}
    for t in unused_teachers:
        teachers_count[t] = 0
    return AnnealingState(state_map, unused_teachers, teachers_count)


def init_state(sch: Schedule):
    sch_state = sch.sch_state
    state = make_state(sch_state)
    for d, day in sch.days.items():
        for p, slot in day.slots.items():
            for event in slot.state:
                g, r, s, t = event.g, event.r, event.s, event.t
                if (s, g) in state.state_map.keys():
                    continue
                if t == -1:
                    t = choice(sch_state.all_teachers)
                state.add(s, g, t)
    return state


class AnnealingState2:
    def copy(self):
        return AnnealingState2(self.state_map, self.schedule)

    def __init__(self, state_map, schedule: Schedule):
        self.state_map = copy(state_map)
        self.schedule = schedule
        self._size_for_good_slots = 10
        self.events_update_chance = {}
        self.origin_slot_by_event = {}
        self.score_by_entity_and_slot = {}
        for l in self.schedule.sch_state.all_lessons:
            _, slot = self.schedule.get_day_and_slot(l)
            for e in slot.state:
                self.events_update_chance[e] = 0
                self.origin_slot_by_event[e] = l

    def slot_by_event(self, e: Event):
        return self.state_map.get(e, self.origin_slot_by_event[e])

    def update(self, e: Event, l: int, chance: int):
        self.events_update_chance[e] = chance
        self.state_map[e] = l

    # needs rework
    def _entity_func_with_cache(self, func: Callable[[tuple[int, int, int, int]], list[int]]) -> \
            tuple[Callable[[tuple[int, int, int, int]], list[int]], Callable[[tuple[int, int, int, int]], None]]:
        cache = {}

        def invalidate(entity):
            cache[entity] = []

        def impl(entity):
            # if entity in cache:
            #     return cache[entity]
            return func(entity)

        return impl, invalidate

    def _good_slots_for_event(self, e: Event) -> list[int]:
        # ans = {}
        # for l in self.schedule.sch_state.all_lessons:
        #     if l == self.slot_by_event(e):
        #         continue
        #     if (e, l) in self.score_by_entity_and_slot.keys():
        #         ans[l] = self.score_by_entity_and_slot[(e, l)]
        conflicts = {}
        for l in self.schedule.sch_state.all_lessons:
            conflicts[l] = 0
        size = self._size_for_good_slots
        for l in self.schedule.sch_state.all_lessons:
            day, slot = self.schedule.get_day_and_slot(l)
            for other_e in slot.state:
                real_l = self.state_map.get(other_e, l)
                conflicts[real_l] += self._conflicts_with_event(e, other_e)
        return list(map(lambda item: item[0], sorted(conflicts.items(), key=lambda item: item[1])))[0:size]
        # return list(map(lambda item: item[0], sorted(ans.items(), key=lambda item: -item[1])))[0:self._size_for_good_slots]

    def _conflicts_with_event(self, e: Event, other_e: Event):
        rating = 0
        if e.num == other_e.num:
            return 0
        if other_e.g == e.g:
            rating += 1
        if other_e.r == e.r:
            rating += 1
        if other_e.t == e.t:
            rating += 1
        return rating

    def events_relation_score(self, e: Event, other_e: Event):
        conflicts = self._conflicts_with_event(e, other_e)
        l = self.slot_by_event(e)
        other_l = self.slot_by_event(other_e)
        day, slot = self.schedule.get_day_and_slot(l)
        other_day, other_slot = self.schedule.get_day_and_slot(other_l)
        if day == other_day:
            diff = abs(l - other_l)
            if diff == 0 and conflicts != 0:
                score = 15 * conflicts
            else:
                score = 3 * diff * (3 - conflicts)
        else:
            score = conflicts
        self.events_update_chance[other_e] += score
        if (other_e, l) not in self.score_by_entity_and_slot.keys():
            self.score_by_entity_and_slot[(other_e, l)] = 0
        self.score_by_entity_and_slot[(other_e, l)] += score

    def events_chance_to_change_process(self):
        # self.score_by_entity_and_slot.clear()
        # for e in self.origin_slot_by_event.keys():
        #     for other_e in self.origin_slot_by_event.keys():
        #         self.events_relation_score(e, other_e)
        events_by_slot = {}
        for e in self.origin_slot_by_event.keys():
            l = self.slot_by_event(e)
            _, slot = self.schedule.get_day_and_slot(l)
            if l not in events_by_slot.keys():
                events_by_slot[l] = []
            events_by_slot[l].append(e)
        for _, day in self.schedule.days.items():
            for _, slot in day.slots.items():
                l = slot.raw_num
                events_in_slot = events_by_slot.get(l, [])
                for i in range(len(events_in_slot)):
                    for j in range(i + 1, len(events_in_slot)):
                        event = events_in_slot[i]
                        other_event = events_in_slot[j]
                        conflicts = self._conflicts_with_event(event, other_event)
                        self.events_update_chance[other_event] += 3 * conflicts

    def events_to_change(self):
        events_to_change = list(
            map(lambda item: item[0], sorted(self.events_update_chance.items(), key=lambda item: -item[1])))[0:5]
        ans = {}
        for e in events_to_change:
            ans[e] = self.slot_by_event(e)
        return ans

    def change_schedule(self):
        n = 0 + 1
        fix = puff

        # for l in self.schedule.sch_state.all_lessons:
        #     _, slot = self.schedule.get_day_and_slot(l)
        #     for e in slot.state:
        #         self.events_update_chance[e] = 0
        self.events_chance_to_change_process()
        change_list = self.events_to_change()
        for event in self.events_update_chance.keys():
            if event not in change_list.keys():
                self.events_update_chance[event] += 0
        # print(self.events_update_chance.values())
        for event_to_change in change_list.keys():
            l = change_list[event_to_change]
            new_slot_list = self._good_slots_for_event(event_to_change)
            new_l = choice(new_slot_list)
            old_chance = self.events_update_chance[event_to_change]
            self.update(event_to_change, new_l, 0)
            fix = self.get_fix(event_to_change, l, old_chance, fix)
            n -= 1
            if n == 0:
                return fix
        return fix

    def get_fix(self, event, l, chance, pref_fix):
        def fix():
            self.update(event, l, chance)
            pref_fix()

        return fix

    def construct_schedule(self):
        updates = []
        for l in self.schedule.sch_state.all_lessons:
            _, old_slot = self.schedule.get_day_and_slot(l)
            for event in old_slot.state:
                if event not in self.state_map.keys():
                    continue
                _, new_slot = self.schedule.get_day_and_slot(self.state_map[event])
                updates.append((event, old_slot, new_slot))
        for update in updates:
            event, old_slot, new_slot = update
            old_slot.remove_event_info(event)
            old_slot.remove_event(event)
            new_slot.add_event_info(event)
            new_slot.add_event(event)


def init_state2(sch: Schedule):
    return AnnealingState2({}, sch)
