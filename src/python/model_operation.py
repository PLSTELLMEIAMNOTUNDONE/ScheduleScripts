from typing import Callable

from ortools.sat.python import cp_model

from src.python.schedule.schedule_state import SchState


def build(state: SchState, schedule: dict, model, fun: Callable):
    fun(state, schedule, model)

    def continue_build(next_fun, end=False):
        if end:
            build(state, schedule, model, next_fun)
            return
        return build(state, schedule, model, next_fun)

    return continue_build


def init_model(state: SchState, schedule: dict, model):
    for r in state.all_rooms:
        for s in state.all_subjects:
            for l in state.all_lessons:
                for g in state.all_groups:
                    for t in state.all_teachers:
                        if state.possible(g, t, r, s, l):
                            schedule[(r, s, l, g, t)] = model.NewBoolVar(
                                f"sch_{state.roomsNames[r]}_{state.subjectsNames[s]}_{state.lessonsNames[l]}_{state.groupsNames[g]}_{state.teachersNames[t]}")


def at_most_one_room_for_time(state: SchState, schedule: dict, model):
    for r in state.all_rooms:
        for l in state.all_lessons:
            model.AddAtMostOne(
                schedule[(r, s, l, g, t)]
                for t in state.all_teachers
                for s in state.all_subjects
                for g in state.all_groups
                if state.possible(g, t, r, s, l)
            )


def at_most_one_group_for_time(state: SchState, schedule: dict, model):
    for g in state.all_groups:
        for l in state.all_lessons:
            model.AddAtMostOne((schedule[(r, s, l, ug, t)] for ug in state.unity[g]
                                for s in state.all_subjects
                                for r in state.all_rooms
                                for t in state.all_teachers
                                if state.possible(ug, t, r, s, l)))


def at_most_one_teacher_for_time(state: SchState, schedule: dict, model):
    for t in state.all_teachers:
        for l in state.all_lessons:
            model.AddAtMostOne((schedule[(r, s, l, g, t)]
                                for g in state.all_groups
                                for s in state.all_subjects
                                for r in state.all_rooms
                                if state.possible(g, t, r, s, l)))


def exact_amount_of_classes_for_group(state: SchState, schedule: dict, model):
    for s in state.all_subjects:
        for g in state.all_groups:
            model.Add(sum(schedule[(r, s, l, g, t)]
                          for r in state.all_rooms
                          for l in state.all_lessons
                          for t in state.all_teachers
                          if state.possible(g, t, r, s, l)) == state.subject_to_group[s][g]
                      )


def one_teacher_for_group_and_subject(state: SchState, schedule: dict, model):
    indix = {}
    for s in state.all_subjects:
        for g in state.all_groups:
            for t in state.all_teachers:
                indix[(s, g, t)] = model.NewBoolVar(f"ind_{[state.subjectsNames[s]]}_{state.groupsNames[g]}")
                model.Add(sum(schedule[(r, s, l, g, t)]
                              for r in state.all_rooms
                              for l in state.all_lessons
                              if state.possible(g, t, r, s, l)) == state.subject_to_group[s][g]
                          ).OnlyEnforceIf(indix[(s, g, t)])

                model.Add(sum(schedule[(r, s, l, g, t)]
                              for r in state.all_rooms
                              for l in state.all_lessons
                              if state.possible(g, t, r, s, l)) == 0
                          ).OnlyEnforceIf(~indix[(s, g, t)])


def clustering(state: SchState, schedule: dict, model):
    indix = {}
    for l in state.all_lessons:
        for g in state.casual_groups_range:
            if l % 5 <= 1:
                continue
            d = l // 5
            indix[(l, g)] = model.NewBoolVar(f"ind_{[l]}_{state.groupsNames[g]}")
            model.AddMaxEquality(indix[(l, g)], [schedule[(r, s, ll, ug, t)]
                                                 for ll in range(d * 5, l - 1)
                                                 for ug in state.unity[g]
                                                 for r in state.all_rooms
                                                 for s in state.all_subjects
                                                 for t in state.all_teachers
                                                 if state.possible(ug, t, r, s, ll)])
            model.Add(indix[(l, g)] - sum(schedule[(r, s, l - 1, ug, t)]
                                          for ug in state.unity[g]
                                          for r in state.all_rooms
                                          for s in state.all_subjects
                                          for t in state.all_teachers
                                          if state.possible(ug, t, r, s, l))
                      + sum(schedule[(r, s, l, ug, t)]
                            for ug in state.unity[g]
                            for r in state.all_rooms
                            for s in state.all_subjects
                            for t in state.all_teachers
                            if state.possible(ug, t, r, s, l)
                            ) <= 1)


def clustering_for_t_v1(state: SchState, schedule: dict, model):
    indix = {}
    for l in state.all_lessons:
        for t in state.all_teachers:
            if l % 5 <= 1:
                continue
            d = l // 5
            indix[(l, t)] = model.NewBoolVar(f"ind_{[l]}_{state.teachersNames[t]}")
            model.AddMaxEquality(indix[(l, t)], [schedule[(r, s, ll, g, t)]
                                                 for ll in range(d * 5, l - 1)
                                                 for g in state.all_groups
                                                 for r in state.all_rooms
                                                 for s in state.all_subjects
                                                 if state.possible(g, t, r, s, ll)])
            model.Add(indix[(l, t)] - sum(schedule[(r, s, l - 1, g, t)]
                                          for g in state.all_groups
                                          for r in state.all_rooms
                                          for s in state.all_subjects
                                          if state.possible(g, t, r, s, l))
                      + sum(schedule[(r, s, l, g, t)]
                            for g in state.all_groups
                            for r in state.all_rooms
                            for s in state.all_subjects
                            if state.possible(g, t, r, s, l)
                            ) <= 1)


def prioritize_start_of_day(state: SchState, schedule: dict, model):
    z = sum(schedule[(r, s, l, g, t)] * ((l + 0) % 5)
            for r in state.all_rooms
            for l in state.all_lessons
            for s in state.all_subjects
            for g in state.all_groups
            for t in state.all_teachers
            if state.possible(g, t, r, s, l)
            )
    model.Minimize(z)


def init(state: SchState, schedule: dict, model):
    print(f"for state: {state} \n  model were build")



def dummy_plausable(r, s, l, g, t):
    return True
