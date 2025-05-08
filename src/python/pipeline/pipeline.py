import time

from annealing.annealing import energy_template_for_at_most_one_check, get_teacher_by_event, get_slot_by_event, \
    annealing_default
from common.json.schedule_parser import map_spbu_data_to_schedule
from schedule.config import fast_test_enable, stop_after_task
from src.python.annealing.annealing import SA_for_teachers
from src.python.common.records.recorder import recorder
from src.python.schedule.schedule import sch, fast_sch
from src.python.schedule.schedule_state import SchState

recorder = recorder("Flow", True)


def execute_task(sch_state):
    if fast_test_enable:
        return fast_sch(sch_state)
    return sch(sch_state)


def process(sch_states: list[SchState]):
    i = 0
    ans = []
    for sch_state in sch_states:
        i += 1
        start = time.time()
        # g, r, s, t
        energy_for_teacher = energy_template_for_at_most_one_check(
            True,
            list(sch_state.teachers.keys()),
            lambda e, a: e.t,
            get_slot_by_event,
        )
        energy_for_group = energy_template_for_at_most_one_check(
            True,
            list(sch_state.groups.keys()),
            lambda e, a: e.g,
            get_slot_by_event,
        )
        energy_for_rooms = energy_template_for_at_most_one_check(
            False,
            list(sch_state.rooms.keys()),
            lambda e, a: e.r,
            get_slot_by_event,
        )
        energy = lambda a_state, sch: energy_for_rooms(a_state, sch) \
                                      + energy_for_group(a_state, sch) \
                                      + energy_for_teacher(a_state, sch)
        recorder.record("Процессинг задачи номер " + str(i))
        schedule, schedule_res = recorder.record_with_time(lambda: execute_task(sch_state))
        recorder.record("Завершился начальный этап")

        # sa_state = SA_for_teachers(schedule=schedule,
        #                              energy_func=energy_for_teacher)
        # recorder.record_with_time(lambda: sa_state.construct_schedule(schedule))
        sa_state = annealing_default(schedule=schedule,
                                     energy_func=energy)

        recorder.record_with_time(lambda: sa_state.construct_schedule())
        end = time.time()
        recorder.record("Завершился второй этап")
        schedule.make_record()
        schedule.windows_for_teachers()
        schedule.windows_for_groups()

        best_energy = energy(sa_state, schedule)
        recorder.record("Энергия итогового расписания " + str(best_energy))
        recorder.record("Размер итогового расписания " + str(schedule.size()))
        recorder.record("Задача решилась за " + str(end - start) + " секунд")

        if stop_after_task:
            while True:
                print("ready to interact")
                params = input().split(' ')
                if len(params) < 2:
                    break
                act, num = params[0], int(params[1])
                ans = schedule.actions_by_name[act](num)
                for k, entities in ans.items():
                    print(k)
                    for entity in entities:
                        g, r, s, t = entity

                        print((sch_state.groups[g], sch_state.teachers[t], sch_state.rooms[r], sch_state.subjects[s]))
        ans.append(best_energy)
    return ans


if __name__ == "__main__":



    tasks = []
    tasks.append(map_spbu_data_to_schedule(f'src\\python\\resources\\test'))
    #
    # with open("medium_case.json") as f:
    #     tasks.append(map_json_to_schedule(f))
    #
    # with open("highly_distributed_case.json") as f:
    #     tasks.append(map_json_to_schedule(f))
    #
    process(tasks)
