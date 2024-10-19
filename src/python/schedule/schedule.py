from src.python.schedule.post_procces.Schedule import Schedule
from src.python.model_operation import *


def sch(state: SchState):
    schedule = {}
    model = cp_model.CpModel()
    build(state=state, model=model, schedule=schedule, fun=init_model)(
        at_most_one_group_for_time)(
        at_most_one_room_for_time)(
        at_most_one_teacher_for_time)(
        one_teacher_for_group_and_subject)(
        clustering)(
        exact_amount_of_classes_for_group)(
        clustering_for_t_v1, end=True
    )

    solver = cp_model.CpSolver()

    solver.parameters.enumerate_all_solutions = False
    status = solver.Solve(model)

    print(solver.SolutionInfo())
    print(solver.ResponseStats())

    if status == cp_model.FEASIBLE:
        print("ok")
    if status == cp_model.INFEASIBLE:
        raise Exception("INFEASIBLE state")

    print(status)
    result = {}
    sss = 0
    for k, v in schedule.items():
        r, s, l, g, t = k

        if solver.Value(v) and (s, g) in state.subject_group_map:
            result[k] = 1
            sss += 1

    # print(sss)

    # fix!

    return Schedule(result,
                    state,
                    6,
                    5,
                    state.subjectsNames,
                    state.groupsNames,
                    state.roomsNames,
                    state.teachersNames
                    ), errors(state, result), errors_for_teachres_v1(state, result), result


# deprecated
def errors(state: SchState, schedule_inst):
    e = 0
    for g in state.all_groups:
        for d in range(0, 6):
            last = -1
            start = False
            for l in range(0, 5):
                exist = (any((r, s, (l + d * 5), g, t) in schedule_inst
                             for r in state.all_rooms
                             for s in state.all_subjects
                             for t in state.all_teachers
                             if state.possible(r, s, l, g, t)))

                if exist and start:
                    if last != l - 1:
                        for i in range(last + 1, l):
                            print("день " + str(d + 1) + " пара " + str(i + 1) + " грyппа " + state.groupsNames[g])
                            e += 1
                    last = l
                    continue
                if exist:
                    start = True
                    last = l

    print("errors for groups = " + str(e))
    return e


def errors_for_teachres_v1(state: SchState, schedule_inst):
    e = 0
    for t in state.all_teachers:
        for d in range(0, 6):
            last = -1
            start = False
            for l in range(0, 5):
                exist = (any((r, s, (l + d * 5), g, t) in schedule_inst
                             for r in state.all_rooms
                             for s in state.all_subjects
                             for g in state.all_groups
                             if state.possible(r, s, l, g, t)))

                if exist and start:
                    if last != l - 1:
                        for i in range(last + 1, l):
                            print(
                                "день " + str(d + 1) + " пара " + str(i + 1) + " преподаватель " + state.teachersNames[t])
                            e += 1
                    last = l
                    continue
                if exist:
                    start = True
                    last = l

    print("errors for teachers = " + str(e))
    return e


# deprecated
def print_sch(state: SchState, result):
    ans = {}
    for l in state.all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in result.items():
        r, s, l, g = k
        ans[l] += state.subjectsNames[s] + " проходит y грyппы " + state.groupsNames[g] + " в кабинете " + \
                  state.roomsNames[r] + "\n"
    for l in state.all_lessons:
        print(ans[l])
