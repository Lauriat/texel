import curses
import math
import numpy as np


class C:
    WHITE = curses.COLOR_WHITE
    BLACK = curses.COLOR_BLACK
    BLUE = curses.COLOR_BLUE
    GREEN = curses.COLOR_GREEN
    YELLOW = curses.COLOR_YELLOW
    MAGENTA = curses.COLOR_MAGENTA
    LIGHT_MAGENTA = 213


class Styles:
    def __init__(self, cellwidth: int, precision: int):
        self.separator: str = "|"
        self.precision: int = precision
        self.init_colors()
        self.width: int = cellwidth
        self.lnwidth: int = None
        self.cell_fmt: str = None
        self.lineno_fmt: str = None

    def init(self, height: int):
        self.lnwidth: int = int(math.log10(height) + 2)
        self.cell_fmt: str = self.get_cell_format_string()
        self.lineno_fmt: str = self.get_lineno_format_string()

    def init_colors(self):
        curses.init_pair(1, C.WHITE, C.BLUE)
        curses.init_pair(2, C.MAGENTA, C.BLACK)
        curses.init_pair(3, C.BLUE, C.BLACK)
        curses.init_pair(4, C.GREEN, C.BLACK)
        curses.init_pair(5, C.BLACK, C.YELLOW)
        curses.init_pair(6, C.LIGHT_MAGENTA, C.BLACK)
        self.c_selection = curses.color_pair(1)
        self.c_sheets = curses.color_pair(2)
        self.c_border = curses.color_pair(3)
        self.c_sheet_selection = curses.A_UNDERLINE | curses.color_pair(6)
        self.c_header = curses.A_UNDERLINE | self.c_border
        self.c_footer = curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4)
        self.c_lineno = self.c_border
        self.c_visual = curses.color_pair(5)

    def get_cell_format_string(self) -> str:
        return "{:>" + f"{self.width}" + "}" + self.separator

    def get_lineno_format_string(self) -> str:
        return "{:>" + f"{self.lnwidth - 1}" + "}" + self.separator

    def get_header_format_string(self, num_cols: int) -> str:
        return ("{:" f"{self.width}" + "}" + self.separator) * num_cols

    def format_footer(self, string: str, width) -> str:
        if len(string) > width:
            string = string[: width - 3] + "..."
        return ("{:>" + f"{width}" + "}").format(string)

    def format_cell(self, x) -> str:
        if isinstance(x, (float, np.floating)):
            x = round(x, self.precision)
        x = str(x)
        if len(x) > self.width:
            x = x[: self.width - 3] + "..."
        return self.cell_fmt.format(x)
