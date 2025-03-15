import time
from typing import Callable

from schedule.config import default_sout, verbose

cache = {}
def session_id():
    if "session_id" in cache:
        return cache["session_id"]
    n = 0
    with open(r"C:\Users\lera\PycharmProjects\ScheduleScripts\src\python\common\records\id.txt", 'r') as f:
        n = int(f.readline())
    with open(r"C:\Users\lera\PycharmProjects\ScheduleScripts\src\python\common\records\id.txt", 'w') as f:
        f.write(str(n + 1))

    cache["session_id"] = n
    return n


def recorder(domain: str, flag: bool):

    if domain in cache:
        return cache[domain]
    recorder_inst = Recorder(domain, flag, session_id())
    cache[domain] = recorder_inst
    return recorder_inst


class Recorder:

    def __init__(self, file_domain: str, records_enable: bool, id: int):
        self.default_file_name = file_domain + "_record_" + str(id) + ".txt"
        #deprecated
        self.records_enable = records_enable
        self.default_out = default_sout


    def record(self, msg, simple_print: bool=default_sout):
        if not self.records_enable:
            return
        elif simple_print:
            print(msg)
        elif verbose:
            with open(r"C:\Users\lera\PycharmProjects\ScheduleScripts\src\python\common\records\log\\" + self.default_file_name, "a+"
                  ,encoding="utf-8") as f:
                f.write(str(msg) + "\n")

    def with_record(self, start_msg: str, end_msg: str, func: Callable):
        self.record(start_msg)
        res = func()
        self.record(end_msg)
        return res

    def record_with_time(self, func: Callable):
        start = time.time()
        result = func()
        end = time.time()
        self.record("метод отработал за " + str(end - start) + " секунд")
        return result
