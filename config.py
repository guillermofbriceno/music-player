#!/usr/bin/python3
import curses

#Database directory
db_dir = "/home/guillermo/bach/Music/Bach/FLAC"

#Keybindings
number_keys = [ord(str(num)) for num in range(9)]

mvmt_keys = {
            'j': 'move_down',
            'k': 'move_up',
            'h': 'move_left',
            'l': 'move_right',
            'n': 'play_track'
            }


#Curses settings
def load_curses_config(stdscr):
    curses.curs_set(False)
    stdscr.nodelay(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, 124)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, 124)
    curses.init_pair(6, 124, curses.COLOR_BLACK)


############
#Don't touch
mvmt_keys = {ord(k): v for k, v in mvmt_keys.items()}
