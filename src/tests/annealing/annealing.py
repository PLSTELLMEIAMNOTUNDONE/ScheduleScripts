import unittest
from src.python.annealing.annealing import *
from src.python.schedule.schedule import *
from src.python.schedule.state_init import *
import sys

class TestAnnealing(unittest.TestCase):

    def test_init_energy(self):
        sch_state = init_sch()

        schedule, e, e2, schedule_res = sch(sch_state)

        schedule.print_sch()

        sa_state = init_state(schedule)
        print(energy(sa_state=sa_state, schedule=schedule))
        sa_state.construct_schedule(schedule=schedule)
        schedule.print_sch()
        print(schedule.windows_for_teachers())


    def test_default_sch_with_default_sa(self):
        sch_state = init_sch()

        schedule, e, e2, schedule_res = sch(sch_state)

        # ? schedule = dict(sorted(sch_result.items(), key=lambda item: item[0][2])) ?
        sa_state = SA_for_teachers(schedule=schedule,
                                   energy_func=energy,
                                   temp_func=temperature,
                                   transition_func=transition)
        # print_sch_w_teachers(sch_state, sa_state, sch_result)
        print(energy(sa_state=sa_state, schedule=schedule))
        # sys.setrecursionlimit(20000)
        sa_state.construct_schedule(schedule=schedule)
        schedule.print_sch()

        print(schedule.windows_for_teachers())