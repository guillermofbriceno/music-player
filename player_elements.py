#!/usr/bin/python3

import sys,os
from curses_elements import *

player_config  = {
        "MUSIC-DIR": "/home/guillermo/programming/music-player/test-music",
        "SCROLL-START": 8
        }

class Tab:
    def __init__(self, config_type, config_attr, stdscr, database):
        self.panes = []
        self.stdscr = stdscr
        self.isActive = False
        self.attr_keys = [] #GENRE, ALBUM, PERFORMER, TRACKS
        self.attr_values = [] #List of genres, List of albums, List of performers, "EMPTY"
        self.filtered_tracks = []
        self.current_pane = 1
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
        pass
    
    def create_single_pane(self, config_attr):
        window_height, window_width, track_filter_key, track_filter_value = config_attr
        self.filtered_tracks = self.database.get_all_tracks_with(track_filter_key, track_filter_value)
        self.attr_keys.append("TRACK")
        self.attr_values.append("Empty")
        pane = Track_Pane(window_height, window_width, window_height - 1, window_width, 0, 0, player_config["SCROLL-START"], self.stdscr)
        pane.refresh()
        pane.activate()
        self.panes.append(pane)

    def render_all_panes(self, full_render=False):
        #full_render must be run at least once
        if full_render:
            attr_values_tmp = []
            for key, pane in zip(self.attr_keys, self.panes):
                if not key == "TRACK":
                    tmp_list  = get_unique_attributes(self.filtered_tracks, key)
                    attr_values_tmp.append(tmp_list)
                    self.filtered_tracks = get_tracks_with(filtered_tracks, key, [tmp_list[pane.selectedpos]])
            attr_values_tmp.append("Empty") #insert empty string in last entry for tracks in next loop
            self.attr_values = attr_values_tmp

        for pane, lst in zip(self.panes, self.attr_values):
            if pane.is_track_pane():
                pane.render(self.filtered_tracks)
            else:
                pane.render(lst)
        
        """
        Non-looped code for 4-pane

        run once, out of this method:
        filtered_tracks = database.get_all_tracks_with("COMPOSER", ["BACH"])

        ONLY on a movement keypress:
        self.genre_list = get_unique_attributes(filtered_tracks, "GENRE")
        self.filtered_tracks = get_tracks_with(filtered_tracks, "GENRE", genre_list[genre_pane.selectedpos])
        self.album_list = get_unique_attributes(filtered_tracks, "ALBUM")
        self.filtered_tracks = get_tracks_with(filtered_tracks, "ALBUM", album_list[album_pane.selectedpos])
        self.performer_list = get_unique_attributes(filtered_tracks, "PERFORMER")
        self.filtered_tracks = get_tracks_with(filtered_tracks, "PERFORM", performer_list[performer_pane.selected_pos])
       
        on a movement keypress AND normal render (for current playing track)
        genre_pane.render(self.genre_list)
        album_pane.render(self.album_list)
        performer_pane.render(self.performer_list)
        track_pane.render(self.filtered_tracks)
        """
        
    def activate_tab(self):
        self.isActive = True

    def deactivate_tab(self):
        self.isActive = False

    def move_up(self):
        for pane in self.panes:
            pane.move_up_one()

    def move_down(self):
        for pane, l in zip(self.panes, self.attr_values):
            if not pane.is_track_pane():
                pane.move_down_one(len(l))
            else:
                pane.move_down_one(len(self.filtered_tracks))

    def move_left(self):
        if not self.current_pane == 1:
            self.panes[self.current_pane].deactivate()
            self.panes[self.current_pane].stop_showing_position()
            self.current_pane -= 1
            self.panes[self.current_pane].activate()

    def move_right(self):
        if not self.current_pane == len(self.panes):
            self.panes[self.current_pane].deactivate()
            self.current_pane += 1
            self.panes[self.current_pane].activate()

    def refresh_panes(self):
        for pane in self.panes:
            pane.refresh()

    def clear_panes(sefl):
        for pane in self.panes:
            pane.clear()

    def search_mode(self):
        while (k != enter):
            
