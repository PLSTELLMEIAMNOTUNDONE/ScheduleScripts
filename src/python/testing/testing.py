import random
import time
from random import choice

from common.json.schedule_parser import map_spbu_data_to_schedule
from common.records.recorder import clear_cache
from pipeline.pipeline import process
from schedule.config import default_weeks
from schedule.schedule_state import SchState
from src.python.common.records.recorder import recorder, session_id

recorder_flow = recorder("Flow", True)
recorder_testing = recorder("Testing", True)
#subject			type	teacher				hours(int)			group
class TestingSampleGenerate:
    def __init__(self, size: int, group_size: int, teacher_size: int, room_size: int):
        self._size = size
        self._id = session_id()
        self._next_sample_id = 0
        self._next_room_id = 0
        self._next_room_id = 0
        self._room_size = room_size
        self._teacher_size = teacher_size
        self._group_size = group_size
        self._possible_hours = [default_weeks * 2]
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

    def _generate_test_rows(self) -> str:
        ans = ""
        hours = choice(self._possible_hours)
        for g in range(0, self._group_size):
            for t in range(0, self._teacher_size):
                sample_id = self._next_sample_id
                self._next_sample_id += 1
                # always new subject so group subject pair are always unique
                ans += f'subject_{sample_id} type_{sample_id} teacher_{t} {hours} group_{g}\n'
        return ans

    def _generate_test_room(self) -> str:
        self._next_room_id += 1
        return f'{self._next_room_id} 30'

    def generate_test_sample(self) -> SchState:
        with open(f'C:\\Users\\lera\\PycharmProjects\\ScheduleScripts\\src\\python\\resources\\test_rooms_{self._id}.txt', 'w+') as f:
            for _ in range(0, self._room_size):
                f.write(self._generate_test_room() + "\n")
        with open(f'C:\\Users\\lera\\PycharmProjects\\ScheduleScripts\\src\\python\\resources\\test_{self._id}.txt', 'w+') as f:
            f.write(self._generate_test_rows() + "\n")
        return map_spbu_data_to_schedule(f'src\\python\\resources\\test_{self._id}', f'src\\python\\resources\\test_rooms_{self._id}')


if __name__ == '__main__':
    size = 2
    group_size = 11
    teacher_size = 11
    room_size = 11

    for t in range(6, teacher_size):
        for g in range(6, group_size):
            for r in range(6, room_size):
                min_in_day = min((2 * g) / 3, t, r)
                total = 2 * g * t
                if total <= min_in_day * 30:
                    sample = TestingSampleGenerate(size, g, t, r).generate_test_sample()
                    print(f"teacher_size: {t}, group_size: {g}, rooms_size: {r}\n")
                    recorder_testing.record(f"teacher_size: {t}, group_size: {g}, rooms_size: {r}")

                    recorder_flow.record(f"teacher_size: {t}, group_size: {g}, rooms_size: {r}\n")
                    recorder_flow.record("Итоговые данные запуска:\n")
                    start = time.time()
                    energy = process([sample])[0]
                    end = time.time()
                    print("process took", end - start)
                    recorder_testing.record("Общие время работы " + str(end - start) + "\n")
                    recorder_testing.record("Энергия " + str(energy) + "\n")
                    print("\n")
                    recorder_flow.record("Общие время работы " + str(end - start))
                    recorder_flow.record("\n\n")
                    clear_cache()
                else:
                    print(g ,t, r, total, min_in_day * 30)


