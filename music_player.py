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
    database = start_database(db_dir, playlists_dir)

    status_bar = Status_Bar("TEST", stdscr, height, width)

    tabs = []
    for tabconf in tabs_config:
        config_attr = [height, width, 
                tabconf.get('include-only'), tabconf.get('exclude'), tabconf.get('filter-keys'), tabconf.get('pane-titles')]
        tmp_tab = Tab(tabconf['tab-type'], config_attr, stdscr, database, status_bar)
        tabs.append(tmp_tab)

    tabs[0].activate_tab()
    member_func('refresh_panes', tabs)
    

    curses.halfdelay(15)
    k = 100
    current_tab = 0

    while(k != ord('q')):
        status_bar.render_bar()

        if k in mvmt_keys:
            member_func(mvmt_keys[k], tabs)
        elif k in number_keys:
            tabs[current_tab].deactivate_tab()
            current_tab = int(chr(k)) - 1
            tabs[current_tab].activate_tab()
            stdscr.erase()
            status_bar.render_bar()

        for tab in tabs:
            tab.render_all_panes(k is not curses.ERR)
            tab.refresh_panes()

        #status_bar(tabs[current_tab].filtered_tracks[0]["PATH"], stdscr, height, width)

        k = stdscr.getch()

def member_func(f, obj_list):
    for obj in obj_list:
        func = methodcaller(f)
        func(obj)

def main():
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(start_player)

if __name__ == "__main__":
    main()
