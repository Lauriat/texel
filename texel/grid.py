import curses
import math

import numpy as np
from typing import Callable, Dict, List, Optional

from .coordinate import Coordinate
from .keys import Keys, Key
from .styles import Styles
from . import utils


class Grid:
    def __init__(self, scr, sheets: Dict[str, np.ndarray], styles: Styles):
        self.scr = scr
        self.sheets: Dict[str, np.ndarray] = sheets
        self.sheetId: int = 0
        self.sheetNames: List[str] = list(self.sheets.keys())
        self.actions: Dict[Key, Callable] = self.get_actions()
        self.styles: Styles = styles
        self.init()

    def init(self):
        self.origin: Coordinate = Coordinate(0, 0)
        self.selected: Coordinate = Coordinate(0, 0)
        self.array: np.ndarray = self.sheets[self.sheetNames[self.sheetId]]
        self.visual: Optional[Coordinate] = None
        self.heigth, self.width = self.array.shape
        self.styles.init(self.heigth)
        self.draw()

    def redraw(self, func, *args, **kwargs) -> Callable:
        def runnable():
            func(*args, **kwargs)
            self.draw()

        return runnable

    def handle_press(self, key: int) -> bool:
        key = Keys.to_key(key)
        if key:
            if key in self.actions:
                self.actions[key]()
            elif key == Keys.QUIT:
                return False
        return True

    def get_actions(self) -> Dict[Key, Callable]:
        return {
            Keys.UP: self.redraw(self.move_vertical, -1),
            Keys.DOWN: self.redraw(self.move_vertical, 1),
            Keys.LEFT: self.redraw(self.move_horizontal, -1),
            Keys.RIGHT: self.redraw(self.move_horizontal, 1),
            Keys.TAB: self.redraw(self.switch_sheet, 1),
            Keys.SHIFT_TAB: self.redraw(self.switch_sheet, -1),
            Keys.VISUAL: self.redraw(self.set_visual),
            Keys.ESC: self.redraw(self.set_visual, reset=True),
            Keys.COPY: self.copy,
            Keys.HELP: self.help,
        }

    def set_visual(self, reset=False):
        self.visual = None if reset else Coordinate(self.selected.x, self.selected.y)

    def copy(self):
        if self.visual is None:
            utils.copy(self.array[self.selected.y, self.selected.x])
        else:
            ymin, ymax = sorted([self.selected.y, self.visual.y])
            xmin, xmax = sorted([self.selected.x, self.visual.x])
            utils.copy(self.array[ymin : ymax + 1, xmin : xmax + 1])
        self.visual = None
        self.draw()
        self.draw_footer("Copied")

    def help(self):
        self.scr.clear()
        self.scr.addstr(0, 0, "Help")
        for i, string in enumerate(utils.HELP, 2):
            if i >= self.scrheight:
                return
            self.scr.addstr(i, 1, string)

    def move_horizontal(self, direction: int):
        self.selected.x = (self.selected.x + direction) % self.width
        if (self.selected.x - self.origin.x) >= self.scrwidth_cells - 2:
            self.origin.x = self.selected.x - self.scrwidth_cells + 2
        elif self.selected.x < self.origin.x:
            self.origin.x = self.selected.x

    def move_vertical(self, direction: int):
        self.selected.y = (self.selected.y + direction) % self.heigth
        if (self.selected.y - self.origin.y) >= self.scrheight - 3:
            self.origin.y = self.selected.y - (self.scrheight - 3) + 1
        elif self.selected.y < self.origin.y:
            self.origin.y = self.selected.y

    def switch_sheet(self, direction: int):
        if len(self.sheetNames) > 1:
            self.sheetId = (self.sheetId + direction) % len(self.sheetNames)
            self.init()

    def set_screen_variables(self):
        self.scrheight, self.scrwidth = self.scr.getmaxyx()
        self.scrwidth_cells = math.ceil(
            (self.scrwidth - self.styles.lnwidth) / (self.styles.width + 1)
        )
        self.num_cols_in_screen = min(self.width - self.origin.x, self.scrwidth_cells)
        self.num_rows_in_screen = min(self.heigth - self.origin.y, self.scrheight - 3)

    def draw_header(self):
        alphas = utils.get_alphas(self.width)
        fmt = self.styles.get_header_format_string(self.num_cols_in_screen)
        header = fmt.format(
            *alphas[self.origin.x : self.origin.x + self.num_cols_in_screen]
        )
        self.scr.addstr(0, self.styles.lnwidth, header, self.styles.c_header)

    def get_cell_style(self, row: int, col: int):
        coord = self.origin + Coordinate(col, row)
        if self.visual is not None:
            if (
                coord.x >= min(self.selected.x, self.visual.x)
                and coord.x <= max(self.selected.x, self.visual.x)
                and coord.y >= min(self.selected.y, self.visual.y)
                and coord.y <= max(self.selected.y, self.visual.y)
            ):
                if coord == self.selected:
                    return self.styles.c_visual | curses.A_UNDERLINE
                return self.styles.c_visual
        if coord == self.selected:
            return self.styles.c_selection
        return (
            curses.A_UNDERLINE
            if (row == self.num_rows_in_screen - 1)
            else curses.A_NORMAL
        )

    def draw_grid(self):
        for row in range(self.num_rows_in_screen):
            self.scr.addstr(
                row + 1,
                0,
                self.styles.lineno_fmt.format(str(row + self.origin.y + 1)),
                self.styles.c_lineno,
            )
            for col in range(self.num_cols_in_screen):
                self.scr.addstr(
                    row + 1,
                    col * (self.styles.width + 1) + self.styles.lnwidth,
                    self.styles.format_cell(
                        self.array[row + self.origin.y, col + self.origin.x],
                    ),
                    self.get_cell_style(row, col),
                )
        self.scr.addstr(row + 2, 0, " " * self.scrwidth)

    def draw_sheets(self):
        sheetPosx = 0
        for i, sheet in enumerate(self.sheetNames):
            if i == self.sheetId:
                style = self.styles.c_sheet_selection
            else:
                style = self.styles.c_sheets
            self.scr.addstr(self.scrheight - 1, sheetPosx, sheet, style)
            sheetPosx += len(sheet) + 1

    def draw_footer(self, string=None):
        string = string or str(self.array[self.selected.y, self.selected.x])
        self.scr.addstr(
            self.scrheight - 2,
            0,
            self.styles.format_footer(string, self.scrwidth),
            self.styles.c_footer,
        )

    def draw(self):
        self.scr.clear()
        self.set_screen_variables()
        self.draw_header()
        self.draw_grid()
        self.draw_footer()
        self.draw_sheets()
