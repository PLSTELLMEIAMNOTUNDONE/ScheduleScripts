import unittest

from src.python.schedule.schedule import *
from utils.utils import init_sch


class TestSchedule(unittest.TestCase):
    def test_default_sch(self):
        state = init_sch()

        schedule, e = sch(state)
        schedule.make_record()
        self.assertEqual(schedule.windows_for_teachers(), 0)
        self.assertEqual(schedule.windows_for_groups(), 0)
        self.assertEqual(schedule.conflicts_in_rooms(), 0)
        self.assertEqual(schedule.conflicts_in_groups(), 0)
        self.assertEqual(schedule.conflicts_in_teachers(), 0)
        self.assertEqual(schedule.size(), 5)
        # print(schedule.windows_for_groups())

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
