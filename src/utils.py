def tuple_to_list_two_dims(tuple) -> list:
    converted = [list(r) for r in tuple]
    return converted


def sign(value):
    """
    その値が正か負であるかの判定
    """
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0