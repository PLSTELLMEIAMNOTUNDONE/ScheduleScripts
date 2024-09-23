import unittest
from src.python.schedule.config import *

from src.python.schedule.state_init import init_state


class TestInit(unittest.TestCase):
    def test_default(self):
        state = init_state()
        self.assertEqual(default_lecture_rooms, state.lecture_rooms)
        self.assertEqual(default_lessons, state.lessons)
        self.assertEqual(default_teachers, state.teachers)
        self.assertEqual(default_subjects, state.subjects)
        self.assertEqual(default_subjectGroup, state.subject_to_group)
        self.assertEqual(default_subGroup, state.sub_groups)
        self.assertEqual(default_lecture_groups, state.lecture_groups)
        self.assertEqual(default_casual_rooms, state.casual_rooms)
        self.assertEqual(default_casual_groups, state.casual_groups)
