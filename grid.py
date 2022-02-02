import curses
import math
import numpy as np
import pyperclip
from functools import partial

import utils
from actions import Keys
from coordinate import Coordinate
from styles import Styles


class Grid:
    def __init__(self, scr, sheets, precision, cellwidth):
        self.scr = scr
        self.sheets = sheets
        self.sheetId = 0
        self.sheetNames = list(self.sheets.keys())
        self.styles = Styles()
        self.sep = "|"
        self.precision = precision
        self.fmtwidth = cellwidth
        self.cellwidth = self.fmtwidth + 1
        self.arrow_actions = self.get_arrow_actions()
        self.init()

    def init(self):
        self.cursor = Coordinate(0, 0)
        self.screen = Coordinate(0, 0)
        self.as_arr = self.sheets[self.sheetNames[self.sheetId]].to_numpy()
        self.heigth, self.width = self.as_arr.shape
        self.lnwidth = int(math.log10(self.heigth) + 2)
        self.cols = utils.get_alphas(self.width)
        self.fmtstr = "{:>" + f"{self.fmtwidth}" + "}" + self.sep
        self.lnfmt = "{:>" + f"{self.lnwidth}" + "}"
        self.visual = None
        self.draw()

    def on_press(self, key):
        key = Keys.to_key(key)
        if key is None:
            return
        if key in self.arrow_actions:
            self.move(key)
        elif key == Keys.VISUAL:
            self.visual = Coordinate(self.cursor.x, self.cursor.y)
            self.draw()
        elif key == Keys.ESC:
            self.visual = None
            self.draw()
        elif key == Keys.COPY:
            self.copy()
        elif key in (Keys.TAB, Keys.SHIFT_TAB):
            self.switch_sheet(key == Keys.TAB)

    def get_arrow_actions(self):
        return {
            Keys.UP: partial(self.move_vertical, -1),
            Keys.DOWN: partial(self.move_vertical, 1),
            Keys.LEFT: partial(self.move_horizontal, -1),
            Keys.RIGHT: partial(self.move_horizontal, 1),
        }

    def format_cell(self, x):
        if isinstance(x, (float, np.floating)):
            x = round(x, self.precision)
        x = str(x)
        if len(x) > self.fmtwidth:
            x = x[: self.fmtwidth - 3] + "..."
        return self.fmtstr.format(x)

    def copy(self):
        if self.visual is None:
            pyperclip.copy(str(self.as_arr[self.cursor.y, self.cursor.x]))
        else:
            minmaxy = sorted([self.cursor.y, self.visual.y])
            minmaxx = sorted([self.cursor.x, self.visual.x])
            selection = self.as_arr[
                minmaxy[0] : minmaxy[1] + 1, minmaxx[0] : minmaxx[1] + 1
            ]
            pyperclip.copy("\n".join(",".join(map(str, e)) for e in selection))
        self.draw_footer("Copied")
        self.visual = None
        self.draw()

    def move(self, key):
        self.arrow_actions[key]()
        self.draw()

    def move_horizontal(self, direction):
        self.cursor.x = (self.cursor.x + direction) % self.width
        if (self.cursor.x - self.screen.x) >= self.scrwidth - 2:
            self.screen.x = self.cursor.x - self.scrwidth + 2
        elif self.cursor.x < self.screen.x:
            self.screen.x = self.cursor.x

    def move_vertical(self, direction):
        self.cursor.y = (self.cursor.y + direction) % self.heigth
        if (self.cursor.y - self.screen.y) >= self.scrheight - 3:
            self.screen.y = self.cursor.y - (self.scrheight - 3) + 1
        elif self.cursor.y < self.screen.y:
            self.screen.y = self.cursor.y

    def switch_sheet(self, forward):
        self.sheetId = (self.sheetId + (1 if forward else -1)) % len(self.sheetNames)
        self.init()

    def set_screen_variables(self):
        self.scrheight, self.fullwidth = self.scr.getmaxyx()
        self.scrwidth = math.ceil((self.fullwidth - self.lnwidth) / self.cellwidth)
        self.num_cols_in_screen = min(self.width - self.screen.x, self.scrwidth)
        self.num_rows_in_screen = min(self.heigth - self.screen.y, self.scrheight - 3)

    def draw_header(self):
        header = (
            ("{:" f"{self.fmtwidth}" + "}" + self.sep) * self.num_cols_in_screen
        ).format(*self.cols[self.screen.x : self.screen.x + self.num_cols_in_screen])
        self.scr.addstr(0, self.lnwidth, header, self.styles.header)

    def get_cell_style(self, row, col):
        coord = self.screen + Coordinate(col, row)
        if self.visual is not None:
            if (
                coord.x >= min(self.cursor.x, self.visual.x)
                and coord.x <= max(self.cursor.x, self.visual.x)
                and coord.y >= min(self.cursor.y, self.visual.y)
                and coord.y <= max(self.cursor.y, self.visual.y)
            ):
                return self.styles.visual
        if coord == self.cursor:
            return self.styles.selection
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
                self.lnfmt.format(str(row + self.screen.y + 1) + self.sep),
                self.styles.lineno,
            )
            for col in range(self.num_cols_in_screen):
                self.scr.addstr(
                    row + 1,
                    col * self.cellwidth + self.lnwidth,
                    self.format_cell(
                        self.as_arr[row + self.screen.y, col + self.screen.x]
                    ),
                    self.get_cell_style(row, col),
                )
        self.scr.addstr(row + 2, 0, " " * self.fullwidth, self.styles.lineno)

    def draw_sheets(self):
        sheetPos = 0
        for i, sheet in enumerate(self.sheetNames):
            if i == self.sheetId:
                self.scr.addstr(
                    self.scrheight - 1,
                    sheetPos,
                    sheet,
                    self.styles.sheet_selection,
                )
            else:
                self.scr.addstr(self.scrheight - 1, sheetPos, sheet, self.styles.sheets)
            sheetPos += len(sheet) + 1

    def draw_footer(self, string=None):
        string = string or str(self.as_arr[self.cursor.y, self.cursor.x])
        self.scr.addstr(
            self.scrheight - 2,
            0,
            ("{:>" + f"{self.fullwidth}" + "}").format(string),
            self.styles.footer,
        )

    def draw(self):
        self.scr.clear()
        self.set_screen_variables()
        self.draw_header()
        self.draw_grid()
        self.draw_footer()
        self.draw_sheets()
