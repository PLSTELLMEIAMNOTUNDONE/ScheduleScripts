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
        recorder.record("конфигурация расписания: " + str(executor_config.flags))
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
                    ), \
        result


def sch(state: SchState):
    executor_config = full_instance()
    return recorder.record_with_time(lambda: calculate_sch_with_cp(state, executor_config))


def fast_sch(state: SchState):
    executor_config = fast_instance()
    return recorder.record_with_time(lambda: calculate_sch_with_cp(state, executor_config))

# deprecated
def print_sch(state: SchState, result):
    recorder.record(readable_sch_state(state, result))


def readable_sch_state(state: SchState, result) -> str:
    ans = {}
    for l in state.all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in result.items():
        r, s, l, g, t = k
        ans[l] += state.subjects[s].name + " проходит y грyппы " + state.groups[g].name + " в кабинете " + \
                  state.rooms[r].name + "\n"
    ans_str = ""
    for l in state.all_lessons:
        ans_str += ans[l]
    return ans_str
