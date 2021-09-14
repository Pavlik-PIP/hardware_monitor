def sensors_dict_to_usual_dict(sensors_dict: dict):
    return_dict = {}

    names = sensors_dict.keys()
    for name in names:
        name_list = []
        for entry in sensors_dict[name]:
            entry_dict = {"label": entry.label, "current": entry.current}
            name_list.append(entry_dict)
        return_dict[name] = name_list

    return return_dict
