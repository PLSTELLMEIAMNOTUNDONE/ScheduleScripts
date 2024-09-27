from src.python.annealing.annealing_state import *
from src.python.schedule.schedule_state import SchState
from src.python.annealing.util import *


# from random import random


#
# cons = {}

#
#

#
#
def energy(sch_state: SchState, sa_state: AnnealingState, result_sch):
    cons = {}
    bad_coef_window = 1
    bad_coef_same_day = 100
    ans = 0
    last_in_day = {}
    for d in range(6):
        last_in_day[d] = [-1 for t in sch_state.all_teachers]
    for l in range(sch_state.lessons):
        for t in range(sch_state.teachers):
            cons[(t, l)] = 0
    for k, v in result_sch.items():
        r, s, l, g = k
        t = sa_state.state_map[(s, g)]
        d = l // 5
        p = l % 5
        cons[(t, l)] += 1
        if cons[(t, l)] > 1:
            ans += bad_coef_same_day * cons[(t, l)]
        if last_in_day[d][t] != -1 and last_in_day[d][t] != p - 1:
            ans += bad_coef_window
        last_in_day[d][t] = p

    return ans


def SA_for_teachers(sch_state: SchState, result_sch, energy_func, temp_func, transition_func, eps=1e-10):
    temp = 100000
    sa_state = init_state(sch_state)
    E = energy_func(sch_state, sa_state, result_sch)
    i = 1
    best_state = sa_state.copy()
    best_E = E
    while temp > eps:
        fix = sa_state.change_state(sch_state)

        new_E = energy_func(sch_state, sa_state, result_sch)
        delt_E = new_E - E
        if delt_E >= 0 and not transition_func(delt_E, temp):
            print("fixed")
            fix()
        else:
            print("changed")
            E = new_E
        if E == 0:
            print("break")
            break
        if E < best_E:
            best_E = E
            best_state = sa_state.copy()
        temp = temp_func(temp, i)
        i += 1
        print(f'step: {i}, enegry : {E}, temp : {temp}')
    return best_state


def print_sch_w_teachers(sch_state: SchState, sa_state: AnnealingState, sch_result):
    ans = {}
    for l in sch_state.all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in sch_result.items():
        r, s, l, g = k

        ans[l] += sch_state.subjectsNames[s] + " проходит y грyппы " + sch_state.groupsNames[g] + " в kабинете " + sch_state.roomsNames[r] + " ведет " + sch_state.teachersNames[sa_state.state_map[(s, g)]] + "\n"

    for l in sch_state.all_lessons:
        print(ans[l])
