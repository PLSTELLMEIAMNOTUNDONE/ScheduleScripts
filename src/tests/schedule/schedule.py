import unittest
from src.python.schedule.schedule import *
from src.python.schedule.state_init import *


class TestSchedule(unittest.TestCase):
    def test_default_sch(self):
        state = init_sch()

        schedule, e, e2, res = sch(state)
        schedule.print_sch()
        print(e)
        print(e2)
        print(schedule.windows_for_teachers())
        print(schedule.windows_for_groups())

    def test_execution_configuration(self):
        config = full_instance()
        last_option = config.exclude_last_option()
        self.assertEqual(last_option.enable, False)
        self.assertEqual(last_option.priority, 8)
        last_option = config.exclude_last_option()
        self.assertEqual(last_option.enable, False)
        self.assertEqual(last_option.priority, 7)
        last_option = config.exclude_last_option()
        self.assertEqual(last_option.enable, False)
        self.assertEqual(last_option.priority, 6)
        last_option = config.exclude_last_option()
        self.assertEqual(last_option.enable, False)
        self.assertEqual(last_option.priority, 5)
