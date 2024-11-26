from src.python.annealing.annealing_state import *
from src.python.schedule.schedule_state import SchState
from src.python.schedule.post_procces.Schedule import Schedule
from src.python.annealing.util import *
from src.python.common.records.recorder import recorder
import time

recorder = recorder("Annealing", True)


def energy_template_for_at_most_one_check(count_windows: bool,
                                          indexes: list[int],
                                          index_for_entity):
    def energy_imp(sa_state: AnnealingState,
                   schedule: Schedule):
        cons = {}
        bad_coef_window = 10
        bad_coef_same_day = 1000
        ans = 0
        last_in_day = {}
        for d in schedule.days.keys():
            last_in_day[d] = {}
            for index in indexes:
                last_in_day[d][index] = -1

        for d, day in schedule.days.items():
            for p, slot in day.slots.items():
                for entity in slot.state:
                    l = slot.raw_num
                    index = index_for_entity(entity, sa_state)
                    if (index, l) not in cons.keys():
                        cons[(index, l)] = 0
                    cons[(index, l)] += 1
                    if cons[(index, l)] > 1:
                        ans += bad_coef_same_day
                    if last_in_day[d][index] != -1 and last_in_day[d][index] < p - 1 and count_windows:
                        ans += bad_coef_window
                    last_in_day[d][index] = p

        return ans

    return energy_imp


# deprecated
def energy(sa_state: AnnealingState,
           schedule: Schedule):
    cons = {}
    bad_coef_window = 10
    bad_coef_same_day = 1000
    ans = 0
    last_in_day = {}
    for d in schedule.days.keys():
        last_in_day[d] = [-1 for _ in schedule.sch_state.all_teachers]

    for d, day in schedule.days.items():
        for p, slot in day.slots.items():
            for entity in slot.state:
                g, r, s, _ = entity
                l = slot.raw_num
                t = sa_state.state_map[(s, g)]
                if (t, l) not in cons.keys():
                    cons[(t, l)] = 0
                cons[(t, l)] += 1
                if cons[(t, l)] > 1:
                    ans += bad_coef_same_day
                if last_in_day[d][t] != -1 and last_in_day[d][t] < p - 1:
                    ans += bad_coef_window
                last_in_day[d][t] = p

    return ans


def get_teacher_by_entity(entity, sa_state: AnnealingState):
    g, r, s, _ = entity
    t = sa_state.state_map[(s, g)]
    return t


def SA_for_teachers(schedule: Schedule,
                    energy_func,
                    eps=1e-1000,
                    temp=1000000):
    sa_state = init_state(schedule)
    E = energy_func(sa_state, schedule)
    transition_func = get_transition_fun()
    temp_func = get_temp_fun()
    i = 1
    best_state = sa_state.copy()
    best_E = E
    while temp > eps:

        start_time = time.time()
        fix = sa_state.change_schedule(schedule)

        new_E = energy_func(sa_state, schedule)
        delt_E = new_E - E
        if delt_E >= 0 and not transition_func(delt_E, temp):
            recorder.record("fixed")
            fix()
        else:
            recorder.record("changed")
            E = new_E
        if E < best_E:
            best_E = E
            best_state = sa_state.copy()
        temp = temp_func(temp, i)
        if best_E == 0:
            recorder.record("break")
            break
        i += 1
        recorder.record(f'step: {i}, enegry : {E}, temp : {temp}, time : {time.time() - start_time}')
    recorder.record(f'step: {i}, enegry : {best_E}, temp : {temp}')
    return best_state
