import curses
import math
import numpy as np
import pyperclip

import utils
from actions import Action, ARROWKEYS, Keys
from coordinate import Coordinate
from functools import partial
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
        self.actions = self.get_arrow_actions()
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

    def get_arrow_actions(self):
        return {
            Action.UP: partial(self.move_vertical, -1),
            Action.DOWN: partial(self.move_vertical, 1),
            Action.LEFT: partial(self.move_horizontal, -1),
            Action.RIGHT: partial(self.move_horizontal, 1),
        }

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

    def on_press(self, key):
        if key in ARROWKEYS:
            self.actions[ARROWKEYS[key]]()
            self.draw()
        elif key == Keys.VISUAL:
            self.visual = Coordinate(self.cursor.x, self.cursor.y)
            self.draw()
        elif key == Keys.ESC:
            if self.visual is not None:
                self.visual = None
                self.draw()
        elif key == Keys.COPY:
            self.copy()
        else:
            if len(self.sheetNames) > 1:
                if key in (Keys.TAB, Keys.N):
                    self.sheetId = (self.sheetId + 1) % len(self.sheetNames)
                    self.init()
                if key in (Keys.SHIFT_TAB, Keys.SHIFT_N):
                    self.sheetId = (self.sheetId - 1) % len(self.sheetNames)
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

    def draw_grid(self):
        for row in range(self.num_rows_in_screen):
            self.scr.addstr(
                row + 1,
                0,
                self.lnfmt.format(str(row + self.screen.y + 1) + self.sep),
                self.styles.lineno,
            )
            for col in range(self.num_cols_in_screen):
                style = (
                    curses.A_UNDERLINE
                    if (row == self.num_rows_in_screen - 1)
                    else curses.A_NORMAL
                )
                if self.visual is not None:
                    coord = self.screen + Coordinate(col, row)
                    if (
                        coord.x >= min(self.cursor.x, self.visual.x)
                        and coord.x <= max(self.cursor.x, self.visual.x)
                        and coord.y >= min(self.cursor.y, self.visual.y)
                        and coord.y <= max(self.cursor.y, self.visual.y)
                    ):
                        style = self.styles.selection
                elif (self.screen + Coordinate(col, row)) == self.cursor:
                    style = self.styles.selection
                self.scr.addstr(
                    row + 1,
                    col * self.cellwidth + self.lnwidth,
                    self.format_cell(
                        self.as_arr[row + self.screen.y, col + self.screen.x]
                    ),
                    style,
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
