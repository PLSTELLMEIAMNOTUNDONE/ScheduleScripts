from src.python.common.records.recorder import recorder
from src.python.schedule.schedule_state import SchState
from src.python.schedule.schedule import sch
from src.python.annealing.annealing import SA_for_teachers, energy
from src.python.annealing.util import *
from src.python.common.json.schedule_parser import map_json_to_schedule
import time

recorder = recorder("Flow", True)


def proccess(sch_states: list[SchState]):
    i = 0
    for sch_state in sch_states:
        i += 1
        start = time.time()
        recorder.record("Процессинг задачи номер " + str(i))
        schedule, e, e2, schedule_res = recorder.record_with_time(lambda: sch(sch_state))
        recorder.record("Завершился начальный этап")
        sa_state = SA_for_teachers(schedule=schedule,
                                   energy_func=energy,
                                   temp_func=temperature,
                                   transition_func=transition)

        recorder.record_with_time(lambda: sa_state.construct_schedule(schedule=schedule))
        end = time.time()
        recorder.record("Завершился второй этап")
        schedule.print_sch()
        schedule.windows_for_teachers()
        schedule.windows_for_groups()

        best_energy = energy(sa_state=sa_state, schedule=schedule)
        recorder.record("Энергия итогового расписания " + str(best_energy))
        recorder.record("Задача решилась за " + str(end - start) + " секунд")


if __name__ == "__main__":
    tasks = []
    with open("/Users/volkovk2003/myself/app/src/python/resources/small_case.json") as f:
        tasks.append(map_json_to_schedule(f))

    with open("/Users/volkovk2003/myself/app/src/python/resources/highly_distributed_case.json") as f:
        tasks.append(map_json_to_schedule(f))

    with open("/Users/volkovk2003/myself/app/src/python/resources/medium_case.json") as f:
        tasks.append(map_json_to_schedule(f))
    proccess(tasks)
