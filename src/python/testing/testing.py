import random
from random import choice

from common.json.schedule_parser import map_spbu_data_to_schedule
from pipeline.pipeline import process
from schedule.config import default_weeks
from schedule.schedule_state import SchState


#subject			type	teacher				hours(int)			group
class TestingSampleGenerate:
    def __init__(self, size: int, group_size: int, teacher_size: int):
        self._size = size
        self._id = random.randint(1, self._size)
        self._next_sample_id = 0
        self._possible_hours = [default_weeks * 2, default_weeks * 3]
        self._possible_groups = [g for g in range(0, group_size)]
        self._possible_teachers = [t for t in range(0, teacher_size)]

    def _generate_test_row(self) -> str:
        hours = choice(self._possible_hours)
        group = choice(self._possible_groups)
        teacher = choice(self._possible_teachers)

        sample_id = self._next_sample_id
        self._next_sample_id += 1
        # always new subject so group subject pair are always unique
        return f'subject_{sample_id} type_{sample_id} teacher_{teacher} {hours} group_{group}'

    def generate_test_sample(self) -> SchState:
        with open(f'C:\\Users\\lera\\PycharmProjects\\ScheduleScripts\\src\\python\\resources\\test_{self._id}.txt', 'w+') as f:
            for _ in range(self._size):
                f.write(self._generate_test_row() + "\n")
        return map_spbu_data_to_schedule(f'src\\python\\resources\\test_{self._id}')


if __name__ == '__main__':
    sample = TestingSampleGenerate(60, 7, 7).generate_test_sample()
    process([sample])


