import json
from types import SimpleNamespace

from schedule.config import default_weeks, real_data
from src.python.common.records.recorder import recorder
from src.python.schedule.pre_process.ScheduleAggregator import ScheduleAggregator, g_id_by_name, t_id_by_name, \
    s_id_by_name
from src.python.schedule.schedule import Schedule
from src.python.schedule.schedule_state import SchState
from src.python.schedule.schedule_state import get_sch_init_state


def possible_for_array(bad_entities):
    def possible(g, t, r, s, l):
        return (g, t, r, s, l) not in bad_entities

    return possible


def map_json_to_schedule(json_data):
    data = json.load(json_data, object_hook=lambda d: SimpleNamespace(**d))

    return get_sch_init_state(data.lecture_rooms,
                              data.casual_rooms,
                              data.teachers,
                              data.subjects,
                              data.lessons,
                              data.casual_groups,
                              )


def map_json_to_group(json_data):
    data = json.load(json_data, object_hook=lambda d: SimpleNamespace(**d))

    return get_sch_init_state(data.lecture_rooms,
                              data.casual_rooms,
                              data.teachers,
                              data.subjects,
                              data.lessons,
                              data.casual_groups
                              )


def parse(line: str) -> list[str]:
    if real_data:
        x = line.split("\t")
    else:
        x = line.replace("\t", ' ').split(' ')

    ans = list(filter(lambda a: a != '', x))
    ans[-1].replace('\n', '')
    return ans


sub_group_name_map = {
    "000122 геометрия лекции 3 группы".replace(' ', ''): ["24.Б07-пу", "24.Б08-пу", "24.Б09-пу"],
    "24\\5190\\1_Поток_Лекции": ["24.Б15-пу", "24.Б16-пу"],
    "1_поток_2024_лекции": ["24.Б04-пу", "24.Б05-пу", "24.Б06-пу"],
    "2_поток_2024_лекции": ["24.Б01-пу", "24.Б02-пу", "24.Б03-пу"],
    "3_поток_2024_лекции": ["24.Б07-пу", "24.Б08-пу", "24.Б09-пу"],
    "24\\5003\\1_Поток_Лекции": ["24.Б11-пу", "24.Б12-пу", "24.Б13-пу"],

    "000122 геометрия лекции 3 группы1".replace(' ', ''): ["24.Б07-пу1", "24.Б08-пу1", "24.Б09-пу1"],
    "24\\5190\\1_Поток_Лекции1": ["24.Б15-пу1", "24.Б16-пу1"],
    "1_поток_2024_лекции1": ["24.Б04-пу1", "24.Б05-пу1", "24.Б06-пу1"],
    "2_поток_2024_лекции1": ["24.Б01-пу1", "24.Б02-пу1", "24.Б03-пу1"],
    "3_поток_2024_лекции1": ["24.Б07-пу1", "24.Б08-пу1", "24.Б09-пу1"],
    "24\\5003\\1_Поток_Лекции1": ["24.Б11-пу1", "24.Б12-пу1", "24.Б13-пу1"]
}


def parse_group_info(line: str) -> tuple[bool, list[str]]:
    line = line.replace("\n", '').replace(' ', '')
    if line in sub_group_name_map.keys():
        return False, sub_group_name_map[line]
    groups = line.split(',')
    return True, groups


def parse_room(line: str) -> list[str]:
    x = line.split("\t")
    room = []
    for y in x:
        room.append(list(filter(lambda a: a != '', y.split(' '))))
    return room


log = recorder("parser", True)


def map_spbu_data_to_schedule(filename: str) -> SchState:
    agg = ScheduleAggregator(30)
    weeks = default_weeks
    possible_events = set()

    def possible(g, t, r, s, l):
        return (g, t, s) in possible_events
    with open('C:\\Users\\lera\\PycharmProjects\\ScheduleScripts\\' + filename + ".txt",
              'r',
              encoding="utf-8") as data:
        for line in data.readlines():

            info = parse(line)
            if len(info) == 0 or len(line) == 0:
                continue
            s_name = info[0]
            t_name = info[2]
            g_real_name = info[4]
            s_hours = int(info[3])
            s_amount = int(s_hours / weeks)
            if s_amount == 0:
                continue

            is_real, g_names = parse_group_info(g_real_name)

            agg.write_teacher(t_name)
            agg.write_subject(s_name, s_amount, [])
            for g_name in g_names:
                agg.write_group(g_name, True, 15)
                if is_real:
                    agg.link_group_subject(s_name, g_name)
                    possible_events.add(
                        (g_id_by_name[g_name], t_id_by_name[t_name], s_id_by_name[s_name]))
            if not is_real:
                sub_groups = []
                for g_name in g_names:
                    sub_groups.append(g_id_by_name[g_name])
                agg.write_group(g_real_name, False, 15 * len(sub_groups), sub_groups)
                agg.link_group_subject(s_name, g_real_name)
                possible_events.add(
                    (g_id_by_name[g_real_name], t_id_by_name[t_name], s_id_by_name[s_name]))

    with open('C:\\Users\\lera\\PycharmProjects\\ScheduleScripts\\src\\python\\resources\\test_rooms.txt',
              'r',
              encoding="utf-8") as data:
        for line in data.readlines():
            for info in parse_room(line):
                if len(info) == 0:
                    continue
                r_name = info[0]
                r_capacity = int(info[1])
                agg.write_room(r_name, r_capacity, [])
    state = agg.finish_aggregation(possible)
    log.record(state)
    return state


def map_schedule_to_json(schedule: Schedule):
    with open("schedule.json", "w+") as f:
        json.dump(schedule.__dict__, f, default=lambda o: '<not serializable>')
