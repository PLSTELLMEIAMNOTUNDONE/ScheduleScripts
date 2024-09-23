import unittest
from src.python.annealing.annealing import *
from src.python.schedule.schedule import *
from src.python.schedule.state_init import *


class TestAnnealing(unittest.TestCase):
    def test_default_sch_with_default_sa(self):
        sch_state = init_sch()

        sch_result, e = sch(sch_state)
        sch_result = dict(sorted(sch_result.items(), key=lambda item: item[0][2]))
        sa_state = SA_for_teachers(sch_state=sch_state, result_sch=sch_result, energy_func=energy, temp_func=temperature, transition_func=transition)
        print_sch_w_teachers(sch_state, sa_state, sch_result)
        print(energy(sch_state, sa_state, sch_result))