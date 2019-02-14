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
from config import *

def start_player(stdscr):
    stdscr.clear()
    stdscr.refresh()

    load_curses_config(stdscr)

    height, width = stdscr.getmaxyx()
    database = start_database(db_dir)

    tabs = []
    for tabconf in tabs_config:
        config_attr = [height, width, 
                tabconf['tab-filter'], tabconf.get('filter-keys'), tabconf.get('pane-titles')]
        tmp_tab = Tab(tabconf['tab-type'], config_attr, stdscr, database)
        tabs.append(tmp_tab)

    tabs[0].activate_tab()
    member_func('refresh_panes', tabs)

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
