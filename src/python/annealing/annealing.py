from src.python.annealing.annealing_state import *
from src.python.schedule.schedule_state import SchState
from src.python.schedule.post_procces.Schedule import Schedule
from src.python.annealing.util import *
import time


# from random import random


#
# cons = {}

def energy(sa_state: AnnealingState,
           schedule: Schedule):
    cons = {}
    bad_coef_window = 1
    bad_coef_same_day = 100
    ans = 0
    last_in_day = {}
    for d in schedule.days.keys():
        last_in_day[d] = [-1 for _ in range(schedule.sch_state.teachers)]

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


def SA_for_teachers(schedule: Schedule,
                    energy_func,
                    temp_func,
                    transition_func,
                    eps=1e-1000,
                    temp=10000):
    sa_state = init_state(schedule)
    E = energy_func(sa_state, schedule)
    i = 1
    best_state = sa_state.copy()
    best_E = E
    while temp > eps:

        start_time = time.time()
        fix = sa_state.change_schedule(schedule)

        new_E = energy_func(sa_state, schedule)
        delt_E = new_E - E
        if delt_E >= 0 and not transition_func(delt_E, temp):
            print("fixed")
            fix()
        else:
            print("changed")
            E = new_E
        if E < best_E:
            best_E = E
            best_state = sa_state.copy()
        temp = temp_func(temp, i)
        if best_E == 0:
            print("break")
            break
        i += 1
        print(f'step: {i}, enegry : {E}, temp : {temp}, time : {time.time() - start_time}')
    return best_state


# deprecated
def print_sch_w_teachers(sch_state: SchState, sa_state: AnnealingState, sch_result):
    ans = {}
    for l in sch_state.all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in sch_result.items():
        r, s, l, g = k

        ans[l] += sch_state.subjectsNames[s] + " проходит y грyппы " + sch_state.groupsNames[g] + " в кабинете " + \
                  sch_state.roomsNames[r] + " ведет " + sch_state.teachersNames[sa_state.state_map[(s, g)]] + "\n"

    for l in sch_state.all_lessons:
        print(ans[l])
