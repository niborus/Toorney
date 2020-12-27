import yaml, os
from customFunctions import diverse


def read_file(path: str):
    if os.path.isfile(path):
        with open(path, "r") as f:
            content = f.read()
        return content
    else:
        return ""


def write_file(path: str, content, attached=False):
    if attached:
        mode = "a"
    else:
        mode = "w"

    with open(path, mode) as file:
        file.write(content)


def edit_yaml(file_path: str, path: list, value, adding=True, in_a_list=False):
    """Removing or Adding an Item from a YAML-File
    The Item can be in a list or standalone"""
    content = yaml.load(read_file(file_path))

    if in_a_list:
        content = diverse.build_path_in_dict(content, path, list)
        leaf_list = diverse.get_element_in_dic(content, path)
        if adding:
            if value not in leaf_list:
                leaf_list.append(value)
        else:
            while value in leaf_list:
                leaf_list.remove(value)
        content = diverse.insert_value_in_dict(content, path, leaf_list)

    else:
        if adding:
            content = diverse.insert_value_in_dict(content, path, value)
        else:
            content = diverse.insert_value_in_dict(content, path, None)

    with open(file_path, "w") as file:
        yaml.dump(content, file)


def write_yaml(file_path: str, content: dict):
    with open(file_path, "w") as file:
        yaml.dump(content, file, default_flow_style=False)
