import unittest

from src.python.schedule.post_procces.Schedule import *
from src.python.common.json.schedule_parser import *
from src.python.schedule.schedule import sch

class TestModelOp(unittest.TestCase):
    def test_serialization(self):
        with open("resources/test_sch.json") as f:
            sch_state = map_json_to_schedule(f)
            self.assertEqual(sch_state.lecture_rooms, 2)
            self.assertEqual(sch_state.teachers, 6)
            self.assertEqual(sch_state.casual_rooms, 0)
            self.assertEqual(sch_state.casual_groups, 2)
            self.assertEqual(sch_state.lecture_groups, 0)
            self.assertEqual(sch_state.sub_groups, [])
            self.assertEqual(sch_state.subjects, 2)
            self.assertEqual(sch_state.lessons, 30)
            self.assertEqual(sch_state.subject_to_group, [
                [1, 2],
                [1, 1]
            ])

    def test_deserialization(self):
        with open("resources/test_sch.json") as f:
            sch_state = map_json_to_schedule(f)
            schedule = sch(sch_state)
            map_schedule_to_json(schedule[0])

