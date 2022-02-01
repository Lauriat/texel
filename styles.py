import curses


class Styles:
    '''
    Must init curses screen first!
    '''

    def __init__(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.bordercolor = curses.color_pair(3)
        self.sheets = curses.color_pair(2)
        self.sheet_selection = curses.A_BOLD | curses.A_UNDERLINE | curses.color_pair(2)
        self.header = curses.A_UNDERLINE | self.bordercolor
        self.lineno = self.bordercolor
        self.selection = curses.color_pair(1)
        self.footer = curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4)
