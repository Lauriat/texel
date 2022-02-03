import curses
import numpy as np


class Styles:
    def __init__(self, precision):
        self.separator = "|"
        self.precision = precision
        self.width = None
        self.lnwidth = None
        self.init_colors()

    def init(self, cellwidth, linenowidth):
        self.width = cellwidth
        self.lnwidth = linenowidth
        self.cell_fmt = self.get_cell_format_string()
        self.lineno_fmt = self.get_lineno_format_string()

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self.c_selection = curses.color_pair(1)
        self.c_sheets = curses.color_pair(2)
        self.c_border = curses.color_pair(3)
        self.c_sheet_selection = curses.A_UNDERLINE | curses.color_pair(4)
        self.c_header = curses.A_UNDERLINE | self.c_border
        self.c_footer = curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4)
        self.c_lineno = self.c_border
        self.c_visual = curses.color_pair(5)

    def get_cell_format_string(self):
        return "{:>" + f"{self.width}" + "}" + self.separator

    def get_lineno_format_string(self):
        return "{:>" + f"{self.lnwidth - 1}" + "}" + self.separator

    def get_header_format_string(self, num_cols):
        return ("{:" f"{self.width}" + "}" + self.separator) * num_cols

    def get_footer_format_string(self, width):
        return "{:>" + f"{width}" + "}"

    def format_cell(self, x):
        if isinstance(x, (float, np.floating)):
            x = round(x, self.precision)
        x = str(x)
        if len(x) > self.width:
            x = x[: self.width - 3] + "..."
        return self.cell_fmt.format(x)
