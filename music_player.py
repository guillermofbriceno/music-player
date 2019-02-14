#!/usr/bin/python3

import sys,os
import curses
from pathlib import Path
import taglib
from subprocess import call
import subprocess
import time
from operator import methodcaller

from database import *
from player_elements import *
from curses_elements import *

def start_player(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(False)
    stdscr.nodelay(0)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, 124)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, 124)
    curses.init_pair(6, 124, curses.COLOR_BLACK)

    height, width = stdscr.getmaxyx()

    database = start_database("/home/guillermo/bach/Music/Bach/FLAC")

    tab_filter = ["COMPOSER", ["Bach"]]
    config_attr = [height, width, tab_filter]
    alltracks_tab = Tab("SINGLE", config_attr, stdscr, database)
    
    tab_filter = ["COMPOSER", ["Bach"]]
    filter_keys = ["GENRE", "ALBUM", "PERFORMER", "TRACK"]
    pane_titles = ["Genre", "Work", "Performer", None]
    config_attr = [height, width, tab_filter, filter_keys, pane_titles]
    genre_tab = Tab("4-PANE", config_attr, stdscr, database)
    
    tabs = [alltracks_tab, genre_tab]
    tabs[0].activate_tab()
    for tab in tabs:
        tab.refresh_panes()

    number_keys = [ord(str(num)) for num in range(9)]
    mvmt_keys = {
            ord('j'): 'move_down',
            ord('k'): 'move_up',
            ord('h'): 'move_left',
            ord('l'): 'move_right',
            ord('n'): 'play_track'
            }

    k = 100
    current_tab = 0

    while(k != ord('q')):
        if k in mvmt_keys:
            member_func(mvmt_keys[k], tabs)
        elif k in number_keys:
            tabs[current_tab].deactivate_tab()
            current_tab = int(chr(k)) - 1
            tabs[current_tab].activate_tab()
            stdscr.erase()

        for tab in tabs:
            tab.render_all_panes(True)
            tab.refresh_panes()

        status_bar("Testing", stdscr, height, width)

        k = stdscr.getch()

def member_func(f, obj_list):
    for obj in obj_list:
        func = methodcaller(f)
        func(obj)

def main():
    curses.wrapper(start_player)

if __name__ == "__main__":
    main()
