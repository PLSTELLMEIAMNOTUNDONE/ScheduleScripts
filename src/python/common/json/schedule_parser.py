import json
from types import SimpleNamespace
from src.python.schedule.schedule_state import get_sch_init_state
from src.python.schedule.schedule import Schedule


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
                              data.lecture_groups,
                              data.subjectGroup,
                              data.subGroup,
                              possible_for_array(data.bad_entites)
                              )


def map_schedule_to_json(schedule: Schedule):
    with open("schedule.json", "w+") as f:
        json.dump(schedule.__dict__, f, default=lambda o: '<not serializable>')
