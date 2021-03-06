#!/usr/bin/python3

import sys,os
import curses
from pathlib import Path
import taglib
from subprocess import call
import subprocess
import time
from operator import methodcaller
import logging

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

    tracktime = database.get_total_track_time()

    #status_bar = Status_Bar("Welcome!", stdscr, height, width)
    status_bar = Status_Bar(str(tracktime), stdscr, height, width)

    seek_bar = Seek_Bar(stdscr, height - 1, width)

    tabs = []
    for tabconf in tabs_config:
        config_attr = [height, width, 
                tabconf.get('include-only'), tabconf.get('exclude'), tabconf.get('filter-keys'), tabconf.get('pane-titles')]
        tmp_tab = Tab(tabconf['tab-type'], config_attr, stdscr, database, status_bar)
        tabs.append(tmp_tab)

    tabs[0].activate_tab()
    member_func('refresh_panes', tabs)
   
    status_bar.set_number_of_tabs(len(tabs))

    curses.halfdelay(ui_config["refresh-delay"])
    curses.mousemask(1)
    k = 100
    current_tab = 0

    while(k != ord('q')):
        status_bar.render_bar()
        seek_bar.draw()

        if k in mvmt_keys:
            member_func(mvmt_keys[k], tabs)
        elif k in number_keys and (int(chr(k)) - 1) < len(tabs):
            tabs[current_tab].deactivate_tab()
            current_tab = int(chr(k)) - 1
            tabs[current_tab].activate_tab()
            stdscr.erase()
            status_bar.set_current_tab(current_tab + 1)
            status_bar.render_bar()
            seek_bar.draw()

        for tab in tabs:
            tab.render_all_panes(k is not curses.ERR)
            tab.refresh_panes()

        status_bar.set_bar_string("DEFAULT")

        k = stdscr.getch()
        if k == curses.KEY_MOUSE:
            try:
                mouse_event = curses.getmouse()
            except:
                pass
            else:
                _, x, y, _, _ = mouse_event
                seek_bar.seek(mouse_event)
            

def member_func(f, obj_list):
    for obj in obj_list:
        func = methodcaller(f)
        func(obj)

def main():
    #logging.basicConfig(filename='log',level=logging.DEBUG)
    #logging.getLogger("mpd").setLevel(logging.WARNING)
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(start_player)
    #database = start_database(db_dir, playlists_dir)

if __name__ == "__main__":
    main()
