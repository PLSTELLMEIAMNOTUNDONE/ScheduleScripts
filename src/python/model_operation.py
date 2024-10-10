from typing import Callable

from ortools.sat.python import cp_model

from src.python.schedule.schedule_state import SchState


def build(state: SchState, plausable, schedule: dict, model, fun: Callable):
    fun(state, plausable, schedule, model)

    def continue_build(next_fun, end=False):
        if end:
            build(state, plausable, schedule, model, next_fun)
            return
        return build(state, plausable, schedule, model, next_fun)

    return continue_build


def init_model(state: SchState, plausable, schedule: dict, model):
    for r in state.all_rooms:
        for s in state.all_subjects:
            for l in state.all_lessons:
                for g in state.all_groups:
                    if plausable(r, s, l, g):
                        schedule[(r, s, l, g)] = model.NewBoolVar(
                            f"sch_{state.roomsNames[r]}_{state.subjectsNames[s]}_{state.lessonsNames[l]}_{state.groupsNames[g]}")


def at_most_one_room_for_time(state: SchState, plausable, schedule: dict, model):
    for r in state.all_rooms:
        for l in state.all_lessons:
            model.AddAtMostOne(
                schedule[(r, s, l, g)]
                for s in state.all_subjects
                for g in state.all_groups
                if plausable(r, s, l, g))


def at_most_one_group_for_time(state: SchState, plausable, schedule: dict, model):
    for g in state.all_groups:
        for l in state.all_lessons:
            model.AddAtMostOne((schedule[(r, s, l, ug)] for ug in state.unity[g]
                                for s in state.all_subjects
                                for r in state.all_rooms
                                if plausable(r, s, l, ug)))


def exact_amount_of_classes_for_group(state: SchState, plausable, schedule: dict, model):
    for s in state.all_subjects:
        for g in state.all_groups:
            model.Add(sum(schedule[(r, s, l, g)]
                          for r in state.all_rooms
                          for l in state.all_lessons
                          if plausable(r, s, l, g)) == state.subject_to_group[s][g]
                      )


def clustering(state: SchState, plausable, schedule: dict, model):
    indix = {}
    for l in state.all_lessons:
        for g in state.casual_groups_range:
            if l % 5 <= 1:
                continue
            d = l // 5
            indix[(l, g)] = model.NewBoolVar(f"ind_{[l]}_{state.groupsNames[g]}")
            model.AddMaxEquality(indix[(l, g)], [schedule[(r, s, ll, ug)]
                                                 for ll in range(d * 5, l - 1)
                                                 for ug in state.unity[g]
                                                 for r in state.all_rooms
                                                 for s in state.all_subjects
                                                 if plausable(r, s, ll, ug)])
            model.Add(indix[(l, g)] - sum(schedule[(r, s, l - 1, ug)]
                                          for ug in state.unity[g]
                                          for r in state.all_rooms
                                          for s in state.all_subjects
                                          if plausable(r, s, l - 1, ug))
                      + sum(schedule[(r, s, l, ug)]
                            for ug in state.unity[g]
                            for r in state.all_rooms
                            for s in state.all_subjects
                            if plausable(r, s, l, ug)) <= 1)


def prioritize_start_of_day(state: SchState, plausable, schedule: dict, model):
    z = sum(schedule[(r, s, l, g)] * ((l + 0) % 5)
            for r in state.all_rooms
            for l in state.all_lessons
            for s in state.all_subjects
            for g in state.all_groups
            if plausable(r, s, l, g))
    model.Minimize(z)


def init(state: SchState, plausable, schedule: dict, model):
    print(f"for state: {state} \n model: {model} were build")
    print(f"in form of schedule: {schedule}")


def dummy_plausable(r, s, l, g):
    return True
def dummy_fun(state: SchState, plausable, schedule: dict, model):
    return