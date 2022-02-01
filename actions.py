import curses
from enum import Enum, auto


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


ARROWKEYS = {
    curses.KEY_UP: Action.UP,
    ord("k"): Action.UP,
    curses.KEY_DOWN: Action.DOWN,
    ord("j"): Action.DOWN,
    curses.KEY_LEFT: Action.LEFT,
    ord("h"): Action.LEFT,
    curses.KEY_RIGHT: Action.RIGHT,
    ord("l"): Action.RIGHT,
}
