from ortools.sat.python import cp_model
from src.python.schedule.state_init import init_state
from src.python.schedule.schedule_state import SchState


def sch(state: SchState):
    schedule = {}
    model = cp_model.CpModel()
    for r in state.casual_rooms_range:
        for s in state.all_subjects:
            for l in state.all_lessons:
                for g in state.casual_groups_range:
                    schedule[(r, s, l, g)] = model.NewBoolVar(
                        f"sch_{state.roomsNames[r]}_{state.subjectsNames[s]}_{state.lessonsNames[l]}_{state.groupsNames[g]}")
    for r in lecture_rooms_range:
        for s in all_subjects:
            for l in all_lessons:
                for g in lecture_groups_range:
                    schedule[(r, s, l, g)] = model.NewBoolVar(
                        f"sch_{roomsNames[r]}_{subjectsNames[s]}_{lessonsNames[l]}_{groupsNames[g]}")

    for r in lecture_rooms_range:
        for l in all_lessons:
            model.AddAtMostOne(schedule[(r, s, l, g)] for s in all_subjects for g in lecture_groups_range)
    for r in casual_rooms_range:
        for l in all_lessons:
            model.AddAtMostOne(schedule[(r, s, l, g)] for s in all_subjects for g in casual_groups_range)
    # for s in all_subjects:
    #     for l in all_lessons:
    #         model.AddAtMostOne((schedule[(r, s, l, g)] for g in all_groups for r in
    #                             (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)))
    for g in all_groups:
        for l in all_lessons:
            model.AddAtMostOne((schedule[(r, s, l, ug)] for ug in unity[g]
                                for s in all_subjects
                                for r in
                                (casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)))

    for s in all_subjects:
        for g in all_groups:
            model.Add(sum(schedule[(r, s, l, g)]
                          for r in
                          (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
                          for l in all_lessons) == subjectGroup[s][g])
    # for k, v in subjectGroupMap.items():
    #     s, g = k
    #     model.Add(sum(
    #         schedule[(r, s, l, g)] for r in (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
    #         for l in all_lessons) == v)

    lessonToOptimize = []
    for l in all_lessons:
        if (l) % 5 > 0 and l != 0:
            lessonToOptimize.append(l)
    indix = {}
    for l in all_lessons:
        for g in casual_groups_range:
            if l % 5 <= 1:
                continue
            d = l // 5
            indix[(l, g)] = model.NewBoolVar(f"ind_{[l]}_{groupsNames[g]}")
            model.AddMaxEquality(indix[(l, g)], [schedule[(r, s, ll, ug)]
                                                 for ll in range(d * 5, l - 1)
                                                 for ug in unity[g]
                                                 for r in (
                                                     casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                                                 for s in all_subjects])
            model.Add(indix[(l, g)] - sum(schedule[(r, s, l - 1, ug)]
                                          for ug in unity[g]
                                          for r in (
                                              casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                                          for s in all_subjects)
                      + sum(schedule[(r, s, l, ug)]
                            for ug in unity[g]
                            for r in (casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                            for s in all_subjects) <= 1)
    # z = sum(sum(schedule[(r, s, l, g)]
    #             for r in (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
    #             for s in all_subjects) * ((l + 0) % 5)
    #         for g in all_groups
    #         for l in lessonToOptimize)
    # model.Minimize(z)
    # model.Add(z <= 10)

    solver = cp_model.CpSolver()

    solver.parameters.enumerate_all_solutions = False
    status = solver.Solve(model)

    # print(solver.SolutionInfo())
    # print(solver.ResponseStats())

    if status == cp_model.FEASIBLE:
        print("ok")
    if status == cp_model.INFEASIBLE:
        print("not ok")

    print(status)
    result = {}
    sss = 0
    for k, v in schedule.items():
        r, s, l, g = k

        if solver.Value(v) and (s, g) in subjectGroupMap:
            result[k] = 1
            sss += 1

    print(sss)

    # fix!
    def errors(schedule_inst):
        e = 0
        for g in casual_groups_range:
            for d in range(0, 6):
                last = -1
                start = False
                for l in range(0, 5):
                    exist = (any((r, s, (l + d * 5), g) in schedule_inst
                                 for r in casual_rooms_range
                                 for s in all_subjects)
                             or any((r, s, (l + d * 5), lg) in schedule_inst and g in subGroup[lg]
                                    for r in lecture_rooms_range
                                    for s in all_subjects
                                    for lg in lecture_groups_range))

                    if exist and start:
                        if last != l - 1:
                            for i in range(last + 1, l):
                                print("день " + str(d + 1) + " пара " + str(i + 1) + " грyппа " + groupsNames[g])
                                e += 1
                        last = l
                        continue
                    if exist:
                        start = True
                        last = l

        print("errors = " + str(e))

    errors(result)
    return result
