import curses


class Key:
    def __init__(self, *values):
        self.values = values
        self._hash = hash(values)
        self._keyset = set(values)

    def __eq__(self, other):
        return self._hash == other._hash

    def __hash__(self):
        return self._hash


class Keys:
    ESC = Key(27)
    TAB = Key(ord("\t"), ord("n"))
    SHIFT_TAB = Key(353, ord("N"))
    VISUAL = Key(ord("v"), ord("V"))
    COPY = Key(ord("c"), ord("y"))
    QUIT = Key(ord("q"))
    UP = Key(curses.KEY_UP, ord("k"))
    DOWN = Key(curses.KEY_DOWN, ord("j"))
    LEFT = Key(curses.KEY_LEFT, ord("h"))
    RIGHT = Key(curses.KEY_RIGHT, ord("l"))
    HELP = Key(ord("?"))
    ALL = [ESC, TAB, SHIFT_TAB, VISUAL, COPY, QUIT, UP, DOWN, LEFT, RIGHT, HELP]
    _id_to_key = {id: key for key in ALL for id in key.values}

    @staticmethod
    def to_key(key: int) -> Key:
        return Keys._id_to_key.get(key)
