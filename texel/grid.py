import curses
import math

import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Optional

from .coordinate import Coordinate
from .keys import Keys, Key
from .styles import Styles
from . import utils


class Grid:
    def __init__(
        self, scr: curses.window, sheets: Dict[str, pd.DataFrame], styles: Styles
    ):
        self.scr: curses.window = scr
        self.sheets: Dict[str, pd.DataFrame] = sheets
        self.sheetId: int = 0
        self.sheetNames: List[str] = list(self.sheets.keys())
        self.actions: Dict[Key, Callable] = self.get_actions()
        self.styles: Styles = styles
        self.init()

    def init(self):
        self.cursor: Coordinate = Coordinate(0, 0)
        self.screen: Coordinate = Coordinate(0, 0)
        self.as_arr: np.ndarray = self.sheets[self.sheetNames[self.sheetId]].to_numpy()
        self.visual: Optional[Coordinate] = None
        self.heigth, self.width = self.as_arr.shape
        self.styles.init(self.heigth)
        self.draw()

    def redraw(self, func, *args, **kwargs) -> Callable:
        def runnable():
            func(*args, **kwargs)
            self.draw()

        return runnable

    def handle_press(self, key: int) -> bool:
        key = Keys.to_key(key)
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
        }

    def set_visual(self, reset=False):
        self.visual = None if reset else Coordinate(self.cursor.x, self.cursor.y)

    def copy(self):
        if self.visual is None:
            utils.copy(self.as_arr[self.cursor.y, self.cursor.x])
        else:
            ymin, ymax = sorted([self.cursor.y, self.visual.y])
            xmin, xmax = sorted([self.cursor.x, self.visual.x])
            utils.copy(self.as_arr[ymin : ymax + 1, xmin : xmax + 1])
        self.visual = None
        self.draw()
        self.draw_footer("Copied")

    def move_horizontal(self, direction: int):
        self.cursor.x = (self.cursor.x + direction) % self.width
        if (self.cursor.x - self.screen.x) >= self.scrwidth_cells - 2:
            self.screen.x = self.cursor.x - self.scrwidth_cells + 2
        elif self.cursor.x < self.screen.x:
            self.screen.x = self.cursor.x

    def move_vertical(self, direction: int):
        self.cursor.y = (self.cursor.y + direction) % self.heigth
        if (self.cursor.y - self.screen.y) >= self.scrheight - 3:
            self.screen.y = self.cursor.y - (self.scrheight - 3) + 1
        elif self.cursor.y < self.screen.y:
            self.screen.y = self.cursor.y

    def switch_sheet(self, direction: int):
        self.sheetId = (self.sheetId + direction) % len(self.sheetNames)
        self.init()

    def set_screen_variables(self):
        self.scrheight, self.scrwidth = self.scr.getmaxyx()
        self.scrwidth_cells = math.ceil(
            (self.scrwidth - self.styles.lnwidth) / (self.styles.width + 1)
        )
        self.num_cols_in_screen = min(self.width - self.screen.x, self.scrwidth_cells)
        self.num_rows_in_screen = min(self.heigth - self.screen.y, self.scrheight - 3)

    def draw_header(self):
        alphas = utils.get_alphas(self.width)
        fmt = self.styles.get_header_format_string(self.num_cols_in_screen)
        header = fmt.format(
            *alphas[self.screen.x : self.screen.x + self.num_cols_in_screen]
        )
        self.scr.addstr(0, self.styles.lnwidth, header, self.styles.c_header)

    def get_cell_style(self, row: int, col: int):
        coord = self.screen + Coordinate(col, row)
        if self.visual is not None:
            if (
                coord.x >= min(self.cursor.x, self.visual.x)
                and coord.x <= max(self.cursor.x, self.visual.x)
                and coord.y >= min(self.cursor.y, self.visual.y)
                and coord.y <= max(self.cursor.y, self.visual.y)
            ):
                return self.styles.c_visual
        if coord == self.cursor:
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
                self.styles.lineno_fmt.format(str(row + self.screen.y + 1)),
                self.styles.c_lineno,
            )
            for col in range(self.num_cols_in_screen):
                self.scr.addstr(
                    row + 1,
                    col * (self.styles.width + 1) + self.styles.lnwidth,
                    self.styles.format_cell(
                        self.as_arr[row + self.screen.y, col + self.screen.x],
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
        string = string or str(self.as_arr[self.cursor.y, self.cursor.x])
        self.scr.addstr(
            self.scrheight - 2,
            0,
            self.styles.get_footer_format_string(self.scrwidth).format(string),
            self.styles.c_footer,
        )

    def draw(self):
        self.scr.clear()
        self.set_screen_variables()
        self.draw_header()
        self.draw_grid()
        self.draw_footer()
        self.draw_sheets()
