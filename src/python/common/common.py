def default_adder(mapp: dict, default):
    func_map = mapp

    def add(key, value):
        if key not in func_map.keys():
            func_map[key] = default
        func_map[key] = func_map[key] + value
        if func_map[key] == default:
            func_map.pop(key)

    return add
