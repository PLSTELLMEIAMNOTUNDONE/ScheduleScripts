from src.python.model_operation import *
from functools import cmp_to_key
from ortools.sat.python.cp_model import CpModel
from src.python.common.records.recorder import recorder

recorder = recorder("Flow", True)


class ExecuteOption:
    def __init__(self, enable: bool, priority: int, method: Callable, name: str):
        self.enable = enable
        self.priority = priority
        self.method = method
        self.name = name

    def __str__(self):
        return "\n опция: " + self.name + (" включена" if self.enable else " выключена")

    def __repr__(self):
        return str(self)


def compare_options(x: ExecuteOption, y: ExecuteOption):
    if x.enable == y.enable:
        return x.priority - y.priority
    if x.enable:
        return 1
    return -1


class ExecutionConfiguration:

    def __init__(self):
        self.flags = []
        self.at_most_one_group_for_time_flag = \
            ExecuteOption(True,
                          1,
                          at_most_one_group_for_time,
                          "at_most_one_group_for_time"
                          )
        self.flags.append(self.at_most_one_group_for_time_flag)
        self.at_most_one_room_for_time_flag = \
            ExecuteOption(True,
                          2,
                          at_most_one_room_for_time,
                          "at_most_one_room_for_time"
                          )
        self.flags.append(self.at_most_one_room_for_time_flag)
        self.at_most_one_teacher_for_time_flag = \
            ExecuteOption(True,
                          4,
                          at_most_one_teacher_for_time,
                          "at_most_one_teacher_for_time"
                          )
        self.flags.append(self.at_most_one_teacher_for_time_flag)
        self.one_teacher_for_group_and_subject_flag = \
            ExecuteOption(True,
                          6,
                          one_teacher_for_group_and_subject,
                          "one_teacher_for_group_and_subject"
                          )
        self.flags.append(self.one_teacher_for_group_and_subject_flag)
        self.clustering_flag = \
            ExecuteOption(True,
                          5,
                          clustering,
                          "clustering"
                          )
        self.flags.append(self.clustering_flag)
        self.exact_amount_of_classes_for_group_flag = \
            ExecuteOption(True,
                          3,
                          exact_amount_of_classes_for_group,
                          "exact_amount_of_classes_for_group"
                          )
        self.flags.append(self.exact_amount_of_classes_for_group_flag)
        self.clustering_for_t_v1_flag = \
            ExecuteOption(True,
                          7,
                          clustering_for_t_v1,
                          "clustering_for_t_v1"
                          )
        self.flags.append(self.clustering_for_t_v1_flag)
        self.prioritize_start_of_day_flag = \
            ExecuteOption(True,
                          8,
                          prioritize_start_of_day,
                          "prioritize_start_of_day"
                          )
        self.flags.append(self.prioritize_start_of_day_flag)

    def configure(self, model: CpModel, state: SchState, schedule: dict):
        config = build(state=state, model=model, schedule=schedule, fun=init_model)
        for option in self.flags:
            if option.enable:
                config(option.method)
        config(init, end=True)

    def exclude_last_option(self) -> ExecuteOption:
        option = sorted(self.flags, key=cmp_to_key(compare_options))[-1]
        option.enable = False
        recorder.record("Опция " + option.name + " с приоритетом " + str(option.priority) + " отключена")
        return option

    def exclude_options_with_high_priority(self, threshold: int):
        for option in self.flags:
            if option.priority >= threshold:
                option.enable = False
                recorder.record("Опция " + option.name + " с приоритетом " + str(option.priority) + " отключена")


def full_instance() -> ExecutionConfiguration:
    return recorder.with_record("создание конфигурации", "конфигурации создана", lambda: ExecutionConfiguration())


def fast_instance() -> ExecutionConfiguration:
    config: ExecutionConfiguration = recorder.with_record("создание конфигурации", "конфигурации создана",
                                                          lambda: ExecutionConfiguration())
    config.exclude_options_with_high_priority(6)
    return config
