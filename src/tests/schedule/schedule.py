import unittest
from src.python.schedule.schedule import *
from src.python.schedule.state_init import *


class TestSchedule(unittest.TestCase):
    def test_default_sch(self):
        state = init_state()

        res, e = sch(state)
        print_sch(state, res)