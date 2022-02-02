import curses
from enum import Enum, auto


class Keys:
    ESC = 27
    TAB = ord("\t")
    SHIFT_TAB = 353
    VISUAL = ord("v")
    N = ord("n")
    SHIFT_N = ord("N")
    COPY = ord("c")
    QUIT = ord("q")


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
