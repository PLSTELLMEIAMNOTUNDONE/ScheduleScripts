import datetime
import time
from typing import Callable

cache = {}


def recorder(domain: str, flag: bool):
    if domain in cache:
        return cache[domain]
    recorder_inst = Recorder(domain, flag)
    cache[domain] = recorder_inst
    return recorder_inst


class Recorder:

    def __init__(self, file_domain: str, records_enable: bool):
        self.default_file_name = file_domain + "_record_" + str(datetime.datetime.now()).replace(" ", "_") + ".txt"
        self.records_enable = records_enable

    def record(self, msg):
        if not self.records_enable:
            return
        with open("/Users/volkovk2003/myself/app/src/records/" + self.default_file_name, "a+") as f:
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
