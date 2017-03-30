def is_indexed_name(name):
    return isinstance(name, int) or (len(name) == 1 and '1' <= name <= '9')
