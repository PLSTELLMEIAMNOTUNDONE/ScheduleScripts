import logging


def default_adder(mapp: dict, default):
    func_map = mapp

    def add(key, value):
        if key not in func_map.keys():
            func_map[key] = default
        func_map[key] = func_map[key] + value
        if func_map[key] == default:
            func_map.pop(key)

    return add


class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a")
        logging.debug("A DEBUG Message")
        logging.info("An INFO")
        logging.warning("A WARNING")
        logging.error("An ERROR")
        logging.critical("A message of CRITICAL severity")

    def info(self, msg):
        logging.info(msg)


if __name__ == "__main__":
    Logger()
