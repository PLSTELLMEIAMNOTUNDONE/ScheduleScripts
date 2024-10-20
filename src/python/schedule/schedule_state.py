from typing import Tuple, Callable


class SchState:
    def __init__(self,
                 lecture_rooms,
                 casual_rooms,
                 teachers,
                 subjects,
                 lessons,
                 casual_groups,
                 lecture_groups,
                 subject_to_group,
                 sub_groups,
                 possible):
        self.possible = possible
        self.unity = {}
        self.united_groups = {}
        for g in range(casual_groups + len(sub_groups)):
            self.unity[g] = [g]
            self.united_groups[g] = [g]
        for ug_i in range(len(sub_groups)):
            ug = ug_i + casual_groups
            for g in sub_groups[ug_i]:
                self.unity[g].append(ug)
                self.united_groups[ug].append(g)

        self.lecture_rooms = lecture_rooms
        self.casual_rooms = casual_rooms
        self.teachers = teachers
        self.subjects = subjects
        self.lessons = lessons
        self.casual_groups = casual_groups
        self.lecture_groups = len(sub_groups)
        self.subject_to_group = subject_to_group
        self.sub_groups = sub_groups
        self.lecture_rooms_range = range(casual_rooms, lecture_rooms + casual_rooms)
        self.casual_rooms_range = range(casual_rooms)
        self.all_subjects = range(subjects)
        self.all_lessons = range(lessons)
        self.lecture_groups_range = range(casual_groups, self.lecture_groups + casual_groups)
        self.casual_groups_range = range(casual_groups)
        self.all_groups = range(self.lecture_groups + casual_groups)
        self.all_rooms = range(lecture_rooms + casual_rooms)
        self.all_teachers = range(teachers)
        self.roomsNames = {}
        self.subjectsNames = {}
        self.lessonsNames = {}
        self.groupsNames = {}
        self.teachersNames = {}

        for r in self.casual_rooms_range:
            self.roomsNames[r] = "cr" + str(r + 1)
        for r in self.lecture_rooms_range:
            self.roomsNames[r] = "lr" + str(r + 1)
        for s in self.all_subjects:
            self.subjectsNames[s] = "s" + str(s + 1)
        for l in self.all_lessons:
            self.lessonsNames[l] = "l" + str(l + 1)
        for g in self.casual_groups_range:
            self.groupsNames[g] = "g" + str(g + 1)
        for ug_i in range(len(sub_groups)):
            self.groupsNames[casual_groups + ug_i] = str([self.groupsNames[g] for g in sub_groups[ug_i]])
        for t in self.all_teachers:
            self.teachersNames[t] = "t" + str(t + 1)

        self.groupsNames[-1] = "no group"
        self.roomsNames[-1] = "no room"
        self.subjectsNames[-1] = "no subject"
        self.teachersNames[-1] = "no teacher"

        self.subject_group_map = {}

        for s in self.all_subjects:
            for g in self.all_groups:
                if subject_to_group[s][g] != 0:
                    self.subject_group_map[(s, g)] = subject_to_group[s][g]

    # !!!!!!!!!!!!!!!!!!!!!
    def sg_possible(self, sg: Tuple[int, int]):
        return True


def dummy(g, t, r, s, l):
    return True


def get_sch_init_state(
        lecture_rooms: int,
        casual_rooms: int,
        teachers: int,
        subjects: int,
        lessons: int,
        casual_groups: int,
        lecture_groups: int,
        subject_to_group: list[list[int]],
        sub_groups: dict[int, list[int]],
        possible: Callable[[int, int, int, int, int], bool]) -> SchState:
    return SchState(lecture_rooms, casual_rooms, teachers, subjects, lessons, casual_groups, lecture_groups,
                    subject_to_group, sub_groups, possible)
