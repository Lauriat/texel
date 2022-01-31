#!/usr/bin/env python

import math
import curses
import pandas as pd
import numpy as np
from numbers import Number
from enum import Enum
from argparse import ArgumentParser
from itertools import count, combinations


class Action(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def __init__(self, x):
        self.isHorizontal = x > 1
        self.isVertical = not self.isHorizontal


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


class Reader:
    def __init__(self, filename, csv_delimiter=","):
        self.filename = filename
        self.csv_delimiter = csv_delimiter
        self.xl = self.read()

    def read(self):
        if self.filename.split(".")[-1] == "csv":
            return self.read_csv()
        else:
            return self.read_excel()

    def read_csv(self):
        return pd.read_csv(self.filename, delimiter=self.csv_delimiter, header=None)

    def read_excel(self):
        return pd.read_excel(self.filename, sheet_name=None, header=None)


class Grid:
    def __init__(self, reader, scr):
        self.reader = reader
        self.scr = scr
        self.sheets = list(reader.xl.keys())
        self.sheetId = 0
        self.precision = 2
        self.fmtwidth = 10
        self.cellwidth = self.fmtwidth + 1
        self.sep = "|"
        self.init()

    def init(self):
        self.x = 0
        self.y = 0
        self.screeny = 0
        self.screenx = 0
        self.xl = self.reader.xl[self.sheets[self.sheetId]]
        self.arr = self.xl.to_numpy()
        self.heigth, self.width = self.xl.shape
        self.idxwidth = int(math.log10(self.heigth) + 2)
        alphaIter = self.getAbcIter()
        self.cols = [next(alphaIter) for _ in range(self.width)]
        self.fmt = "{:>" + f"{self.fmtwidth}" + "}" + self.sep
        self.width_char = self.cellwidth * self.width + self.idxwidth
        self.draw()

    def formatValue(self, x):
        if isinstance(x, Number):
            if not isinstance(x, (int, np.integer)):
                x = round(x, self.precision)
        x = str(x)
        if len(x) > self.fmtwidth:
            x = x[: self.fmtwidth - 3] + "..."
        return self.fmt.format(x)

    def getAbcIter(self):
        alpha = range(65, 91)
        for i in count(1):
            chars = combinations(alpha, i)
            for ch in chars:
                yield "".join(map(chr, ch))

    def on_press(self, key):
        if key in ARROWKEYS:
            action = ARROWKEYS[key]
            if action == Action.UP:
                self.y = (self.y - 1) % self.heigth
            elif action == Action.DOWN:
                self.y = (self.y + 1) % self.heigth
            elif action == Action.LEFT:
                self.x = (self.x - 1) % self.width
            elif action == Action.RIGHT:
                self.x = (self.x + 1) % self.width
            if action.isHorizontal:
                if (self.x - self.screenx) >= self.scrwidth - 2:
                    self.screenx = self.x - self.scrwidth + 2
                elif self.x < self.screenx:
                    self.screenx = self.x
            else:
                if (self.y - self.screeny) >= self.scrheight - 3:
                    self.screeny = self.y - (self.scrheight - 3) + 1
                elif self.y < self.screeny:
                    self.screeny = self.y
            self.draw()
        else:
            if key == ord("\t"):
                self.sheetId = (self.sheetId + 1) % len(self.sheets)
                self.init()
            if key == 353:
                self.sheetId = (self.sheetId - 1) % len(self.sheets)
                self.init()

    def draw(self):
        self.scr.clear()
        self.scrheight, self.fullwidth = self.scr.getmaxyx()
        self.scrwidth = math.ceil((self.fullwidth - self.idxwidth) / self.cellwidth)
        ww = min(self.width - self.screenx, self.scrwidth)
        header = (("{:" f"{self.fmtwidth}" + "}" + self.sep) * ww).format(
            *self.cols[self.screenx : self.screenx + ww]
        )
        self.scr.addstr(
            0, self.idxwidth, header, curses.A_UNDERLINE | curses.color_pair(3)
        )
        self.draw_grid()
        fw = "{:>" + f"{self.fullwidth}" + "}"
        selval = str(self.arr[self.y][self.x])
        self.scr.addstr(
            self.scrheight - 2,
            0,
            fw.format(selval),
            curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4),
        )
        w = 0
        for i, sheet in enumerate(self.sheets):
            if i == self.sheetId:
                self.scr.addstr(
                    self.scrheight - 1,
                    w,
                    sheet,
                    curses.A_BOLD | curses.A_UNDERLINE | curses.color_pair(2),
                )
            else:
                self.scr.addstr(self.scrheight - 1, w, sheet, curses.color_pair(2))
            w += len(sheet) + 1

    def draw_grid(self):
        for row in range(min(self.heigth - self.screeny, self.scrheight - 3)):
            ee = "{:>" + f"{self.idxwidth}" + "}"
            self.scr.addstr(
                row + 1,
                0,
                ee.format(str(row + self.screeny + 1) + self.sep),
                curses.color_pair(3),
            )
            for col in range(min(self.width - self.screenx, self.scrwidth)):
                stringi = self.formatValue(
                    self.arr[row + self.screeny, col + self.screenx]
                )
                if (col + self.screenx == self.x) and (row + self.screeny == self.y):
                    self.scr.addstr(
                        row + 1,
                        col * self.cellwidth + self.idxwidth,
                        stringi,
                        curses.color_pair(1),
                    )
                else:
                    if row == self.scrheight - 4:
                        self.scr.addstr(
                            row + 1,
                            col * self.cellwidth + self.idxwidth,
                            stringi,
                            curses.A_UNDERLINE,
                        )
                    else:
                        self.scr.addstr(
                            row + 1,
                            col * self.cellwidth + self.idxwidth,
                            stringi,
                        )


def main(scr, rd):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    grid = Grid(rd, scr)
    while True:
        key = scr.getch()
        if key == ord("q"):
            break
        grid.on_press(key)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "file",
        help="Spreadsheet path (csv, xls, xlsx, xlsm, xlsb, odf, ods or odt)",
        metavar="FILE",
    )
    try:
        args = parser.parse_args()
        rd = Reader(args.file)
    except TypeError:
        parser.print_help()
        exit()
    except FileNotFoundError:
        print("Cannot find or open {}".format(args.file))
        exit()
    curses.wrapper(main, rd)
