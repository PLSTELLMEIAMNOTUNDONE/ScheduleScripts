import unittest
from src.python.schedule.schedule import *
from src.python.schedule.state_init import *


class TestSchedule(unittest.TestCase):
    def test_default_sch(self):
        state = init_sch()

        schedule, e, res = sch(state)
        schedule.print_sch()
        print(e)

