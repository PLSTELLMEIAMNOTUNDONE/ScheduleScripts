import unittest

from src.python.annealing.annealing import *
from src.python.schedule.schedule import *
from utils.utils import init_sch


class TestAnnealing(unittest.TestCase):
    def test_default_sch_with_default_sa(self):
        sch_state = init_sch()

        schedule, e = sch(sch_state)

        energy_func = energy_template_for_at_most_one_check(
            True,
            list(sch_state.teachers.keys()),
            get_teacher_by_entity
        )
        sa_state = SA_for_teachers(schedule=schedule,
                                   energy_func=energy_func)
        problems_by_energy_func = energy_func(sa_state=sa_state, schedule=schedule)
        # sys.setrecursionlimit(20000)
        sa_state.construct_schedule(schedule=schedule)

        self.assertEqual(problems_by_energy_func, schedule.windows_for_teachers())

    def test_fast_sch_with_default_sa(self):
        sch_state = init_sch()

        schedule, e = fast_sch(sch_state)
        energy_func = energy_template_for_at_most_one_check(
            True,
            list(sch_state.teachers.keys()),
            get_teacher_by_entity
        )
        sa_state = SA_for_teachers(schedule=schedule,
                                   energy_func=energy_func)

        problems_by_energy_func = energy_func(sa_state=sa_state, schedule=schedule)

        sa_state.construct_schedule(schedule=schedule)

        self.assertEqual(problems_by_energy_func, schedule.windows_for_teachers())
