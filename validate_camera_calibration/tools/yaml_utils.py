import numpy as np


def numpy_to_yaml_dict(x: np.ndarray) -> dict:
    assert len(x.shape) == 2, "Expected numpy object to be 2d!"
    data = dict()
    data["rows"] = x.shape[0]
    data["cols"] = x.shape[1]
    data["data"] = x.flatten().tolist()
    return data


def yaml_dict_to_numpy(d: dict) -> np.ndarray:
    assert isinstance(d, dict), "Expected yaml dict to be a dict!"
    assert "rows" in d, "Expected 'rows' in yaml dict!"
    assert "cols" in d, "Expected 'cols' in yaml dict!"
    assert "data" in d, "Expected 'data' in yaml dict!"
    assert isinstance(d["rows"], int), "Expected 'rows' to be an integer!"
    assert isinstance(d["cols"], int), "Expected 'cols' to be an integer!"
    assert isinstance(d["data"], list), "Expected 'data' to be a list!"
    rows = d["rows"]
    cols = d["cols"]
    data = d["data"]
    assert (
        len(data) == rows * cols
    ), f"Expected 'data' to be of size {rows*cols}, but is of length {len(data)}!"
    x = np.array(data).reshape([rows, cols])
    return x


def yaml_list_to_numpy(d: list) -> np.ndarray:
    assert isinstance(d, list), "Expected yaml list to be a list!"

    x = np.vstack(d)
    return x


def yaml_to_numpy(y) -> np.ndarray:
    if isinstance(y, dict):
        return yaml_dict_to_numpy(y)
    elif isinstance(y, list):
        return yaml_list_to_numpy(y)
    else:
        raise ValueError(
            f"Expected yaml object to be a dict or list, but is {type(y)}!"
        )
