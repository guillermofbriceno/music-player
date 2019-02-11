#!/usr/bin/python3

import sys,os
from curses_elements import *

player_config  = {
        "MUSIC-DIR": "/home/guillermo/programming/music-player/test-music",
        "SCROLL-START": 8
        }

class Tab:
    def __init__(self, config_type, config_attr, stdscr):
        self.panes = []
        self.stdscr = stdscr
        self.isActive = False
        
        if config_type == "SINGLE":
            create_single_pane(config_attr)
        elif config_type == "4-PANE":
            create_4_pane(config_attr)
        elif config_type == "2-PANE":
            pass
        else:
            raise ValueError("Invalid config type")

    def create_4_pane(self, config_attr):
        pass
    
    def create_single_pane(self, config_attr):
        window_height, window_widthstd = config_attr
        tab = Track_Pane(window_height, window_width, window_height - 1, window_width, 0, 0, player_config["SCROLL-START"], self.stdscr)
        tab.refresh()
        tab.activate()
        self.panes.append(tab)

    def render(self, lists):
        for l, pane in zip(lists, self.panes):
            pane.render(l)

    def refresh(self):
        for pane in self.panes:
            pane.refresh()

    def move_up(self):
        pass

    def move_down(self):
        pass

    def move_left(self):
        pass

    def move_right(self):
        pass
