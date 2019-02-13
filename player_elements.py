#!/usr/bin/python3

import sys,os
from curses_elements import *
from database import *

player_config  = {
        "MUSIC-DIR": "/home/guillermo/programming/music-player/test-music",
        "SCROLL-START": 8
        }

class Tab:
    def __init__(self, config_type, config_attr, stdscr, database):
        self.panes = []
        self.pane_titles = []
        self.stdscr = stdscr
        self.isActive = False
        self.attr_keys = [] #GENRE, ALBUM, PERFORMER, TRACKS (Given)
        self.attr_values = [] #List of genres, List of albums, List of performers, "EMPTY" (Generated)
        self.filtered_tracks = []
        self.main_filter = [] #Main filter for the tab
        self.current_pane = 0
        self.database = database

        if config_type == "SINGLE":
            self.create_single_pane(config_attr)
        elif config_type == "4-PANE":
            self.create_4_pane(config_attr)
        elif config_type == "2-PANE":
            raise NotImplementedError("Config type " + config_type + " not implemented")
        else:
            raise ValueError("Invalid config type")

    def create_4_pane(self, config_attr):
        window_height, window_width, self.main_filter, self.attr_keys, self.pane_titles = config_attr
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1])

        pane1 = List_Pane(window_height, window_width, #main window dims
                window_height - 1, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                player_config["SCROLL-START"], self.stdscr, self.pane_titles[0])

        pane2 = List_Pane(window_height, window_width, 
                window_height - 1, 60, 
                0, 29, 
                player_config["SCROLL-START"], self.stdscr, self.pane_titles[1])

        pane3 = List_Pane(window_height, window_width, 
                9, window_width - 88, 
                0, 88, 
                player_config["SCROLL-START"], self.stdscr, self.pane_titles[2])

        pane4 = Track_Pane(window_height, window_width, 
                window_height - 9, window_width - 88, 
                8, 88, 
                player_config["SCROLL-START"], self.stdscr)

        pane1.activate()
        self.panes = [pane1, pane2, pane3, pane4]
        self.refresh_panes()
        self.populate_lists()

    def create_single_pane(self, config_attr):
        window_height, window_width, self.main_filter = config_attr
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1])
        self.attr_keys.append("TRACK")
        self.attr_values.append("Empty")
        pane = Track_Pane(window_height, window_width, window_height - 1, window_width, 0, 0, player_config["SCROLL-START"], self.stdscr)
        pane.refresh()
        pane.activate()
        self.panes.append(pane)

    def populate_lists(self):
        #this func must be run at least once in the beginning
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1])
        attr_values_tmp = []
        for key, pane in zip(self.attr_keys, self.panes):
            if not key == "TRACK":
                tmp_list = get_unique_attributes(self.filtered_tracks, key)
                attr_values_tmp.append(tmp_list)
                self.filtered_tracks = get_tracks_with(self.filtered_tracks, key, [tmp_list[pane.selectedpos]])
        attr_values_tmp.append("Empty") #insert empty string in last entry for tracks in next loop
        self.attr_values = attr_values_tmp

    def render_all_panes(self, full_render=False):
        if self.isActive:
            if full_render:
                self.populate_lists()

            for pane, lst in zip(self.panes, self.attr_values):
                if pane.is_track_pane():
                    pane.render(self.filtered_tracks)
                else:
                    pane.render(lst)
               
    def activate_tab(self):
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1])
        self.isActive = True

    def deactivate_tab(self):
        self.isActive = False
        del self.filtered_tracks

    def move_up(self):
        if self.isActive:
            for pane in self.panes:
                pane.move_up_one()

    def move_down(self):
        if self.isActive:
            for pane, l in zip(self.panes, self.attr_values):
                if not pane.is_track_pane():
                    pane.move_down_one(len(l))
                else:
                    pane.move_down_one(len(self.filtered_tracks))

    def move_left(self):
        if not self.current_pane == 0 and self.isActive:
            self.panes[self.current_pane].deactivate()
            self.panes[self.current_pane].stop_showing_position()
            self.panes[self.current_pane].clear()
            self.current_pane -= 1
            self.panes[self.current_pane].activate()

    def move_right(self):
        if not self.current_pane == len(self.panes) - 1 and self.isActive:
            self.panes[self.current_pane].deactivate()
            self.current_pane += 1
            self.panes[self.current_pane].activate()

    def refresh_panes(self):
        if self.isActive:
            for pane in self.panes:
                pane.refresh()

    def clear_panes(sefl):
        for pane in self.panes:
            pane.clear()

    def search_mode(self):
        while (k != enter):
            pass
