from src.python.schedule.execution_configurator import full_instance, fast_instance
from src.python.schedule.post_procces.Schedule import Schedule
from src.python.model_operation import *
from src.python.common.records.recorder import recorder
from src.python.schedule.config import default_time_out, fallback_enable

recorder = recorder("schedule_state", True)


def calculate_sch_with_cp(state: SchState, executor_config):
    recorder.record("start process")
    schedule = {}
    model = cp_model.CpModel()
    executor_config.configure(model, state, schedule)

    solver = cp_model.CpSolver()

    solver.parameters.enumerate_all_solutions = False
    solver.parameters.max_time_in_seconds = default_time_out
    status = solver.Solve(model)

    recorder.record(solver.SolutionInfo())
    recorder.record(solver.ResponseStats())
    # timeout
    if status == cp_model.UNKNOWN or status == cp_model.INFEASIBLE:
        if not fallback_enable:
            raise Exception("TIMEOUT")
        recorder.record("scheduling fallback")
        executor_config.exclude_last_option()
        return recorder.record_with_time(lambda: calculate_sch_with_cp(state, executor_config))
    if status == cp_model.FEASIBLE:
        recorder.record("finish initial cp scheduling")
    if status == cp_model.INFEASIBLE:
        raise Exception("INFEASIBLE state")

    recorder.record(status)
    result = {}
    sss = 0
    for k, v in schedule.items():
        r, s, l, g, t = k

        if solver.Value(v) and (s, g) in state.subject_group_map:
            result[k] = 1
            sss += 1

    recorder.record("итоговая конфигурация расписания: " + str(executor_config.flags))
    print_sch(state, result)

    return Schedule(result,
                    state,
                    6,
                    5,
                    state.subjectsNames,
                    state.groupsNames,
                    state.roomsNames,
                    state.teachersNames
                    ), \
        errors(state, result), \
        errors_for_teachres_v1(state, result), \
        result


def sch(state: SchState):
    executor_config = full_instance()
    return recorder.record_with_time(lambda: calculate_sch_with_cp(state, executor_config))


def fast_sch(state: SchState):
    executor_config = fast_instance()
    return recorder.record_with_time(lambda: calculate_sch_with_cp(state, executor_config))


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
                            # !!!!!!!!!!!!!!!!!!!!!!!!!!!
                            # print("день " + str(d + 1) + " пара " + str(i + 1) + " грyппа " + state.groupsNames[g])
                            e += 1
                    last = l
                    continue
                if exist:
                    start = True
                    last = l

    recorder.record("errors for groups = " + str(e))
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
                            recorder.record(
                                "день " + str(d + 1) + " пара " + str(i + 1) + " преподаватель " + state.teachersNames[
                                    t])
                            e += 1
                    last = l
                    continue
                if exist:
                    start = True
                    last = l

    recorder.record("errors for teachers = " + str(e))
    return e


# deprecated
def print_sch(state: SchState, result):
    recorder.record(readable_sch_state(state, result))


def readable_sch_state(state: SchState, result) -> str:
    ans = {}
    for l in state.all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in result.items():
        r, s, l, g, t = k
        ans[l] += state.subjectsNames[s] + " проходит y грyппы " + state.groupsNames[g] + " в кабинете " + \
                  state.roomsNames[r] + "\n"
    ans_str = ""
    for l in state.all_lessons:
        ans_str += ans[l]
    return ans_str
