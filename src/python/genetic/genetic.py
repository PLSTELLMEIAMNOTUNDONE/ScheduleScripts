# идея с чанками
from schedule.post_procces.Schedule import Schedule, MutableSchedule, Slot, empty_slot
from schedule.schedule_state import SchState


def genetic_cycle(
        sch_s: list[Schedule],
        actual_state: SchState,
        m: int = 2,
):
    excluded_entities = []
    sch = sch_s[0]
    for i in range(1, len(sch_s)):
        sch, excluded_entities = cross(sch_s[i], sch, actual_state, excluded_entities)
    return sch, excluded_entities


def cross(sch_1: MutableSchedule, sch_2: MutableSchedule, sch_state: SchState, excluded_entities=None):
    if excluded_entities is None:
        excluded_entities = []
    if sch_1.days_num != sch_2.days_num or sch_2.slots_num != sch_1.slots_num:
        raise Exception("размерности расписаний не совпадают")

    days_num = sch_1.days_num
    slots_num = sch_1.slots_num
    new_sch = MutableSchedule(days_num, slots_num)

    for l in range(1, days_num * slots_num):
        day_num, slot_num = sch_1.get_day_and_slot(l)
        slot_1 = sch_1[day_num][slot_num]
        slot_2 = sch_2[day_num][slot_num]
        new_slot, new_excluded_entities = cross_slot(slot_1, slot_2)
        excluded_entities.extend(new_excluded_entities)
        fixed_slot, excluded_entities = fix_excluded_entities(new_slot, excluded_entities, sch_state)
        new_sch[day_num][slot_num] = fixed_slot
    sch_info = {}
    for l in range(1, days_num * slots_num):
        day_num, slot_num = sch_1.get_day_and_slot(l)
        slot = new_sch[day_num][slot_num]
        fixed_slot, excluded_entities = fix_excluded_entities(slot, excluded_entities, sch_state)
        new_sch[day_num][slot_num] = fixed_slot
        for e in fixed_slot.state:
            g, r, s, t = e
            sch_info[(r, s, l, g, t)] = 1

    return Schedule(sch_info, sch_state, days_num, slots_num), excluded_entities


def fix_excluded_entities(slot: Slot, excluded_entities, sch_state: SchState):
    available_rooms = list(filter(lambda room: not room in slot.rooms.keys(), sch_state.rooms.keys()))
    still_excluded_entities = []
    for entity in excluded_entities:
        g, r, s, t = entity
        found = False
        for new_r in available_rooms:
            if sch_state.possible(g, t, new_r, s, slot.raw_num) \
                    and not g in slot.groups.keys() \
                    and not t in slot.teachers.keys():
                slot.add_entity(g, new_r, s, t)
                found = True
                break
        if not found:
            still_excluded_entities.append(entity)
    return slot, still_excluded_entities


def cross_slot(slot_1: Slot, slot_2: Slot):
    new_slot = empty_slot(slot_1.num + 1, slot_1.raw_num)
    excluded_entities = []
    for entity in slot_1.state:
        g, r, s, t = entity
        if (not r in new_slot.rooms.keys()
                and not g in new_slot.groups.keys()
                and not t in new_slot.teachers.keys()):
            new_slot.add_entity(g, r, s, t)
        else:
            excluded_entities.append((g, r, s, t))
    for entity in slot_2.state:
        g, r, s, t = entity
        if (not r in new_slot.rooms.keys()
                and not g in new_slot.groups.keys()
                and not t in new_slot.teachers.keys()):
            new_slot.add_entity(g, r, s, t)
        else:
            excluded_entities.append((g, r, s, t))
    return new_slot, excluded_entities


def cross_sch_state(sch_state_1: SchState, sch_state_2: SchState):
    def possible(g, t, r, s, l):
        return sch_state_1.origin_possible(g, t, r, s, l) or sch_state_2.origin_possible(g, t, r, s, l)

    teachers = {}
    groups = {}
    rooms = {}
    subjects = {}

    for t in sch_state_1.all_teachers:
        teachers[t] = sch_state_1.teachers[t]
    for g in sch_state_1.groups:
        groups[g] = sch_state_1.groups[g]
    for s in sch_state_1.subjects:
        subjects[s] = sch_state_1.subjects[s]
    for r in sch_state_1.rooms:
        rooms[r] = sch_state_1.rooms[r]

    for t in sch_state_2.all_teachers:
        teachers[t] = sch_state_2.teachers[t]
    for g in sch_state_2.groups:
        groups[g] = sch_state_2.groups[g]
    for s in sch_state_2.subjects:
        subjects[s] = sch_state_2.subjects[s]

    return SchState(
        teachers=teachers,
        groups=groups,
        rooms=rooms,
        subjects=subjects,
        possible=possible,
        lessons=30
    )
