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
        self.attr_keys = [] #GENRE, ALBUM, PERFORMER, TRACKS
        self.attr_values = [] #"Cantatas", "BWV 1", "English Baroque Soloists"
        self.filtered_tracks = []

        if config_type == "SINGLE":
            create_single_pane(config_attr)
            #set filtered tracks to something
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
        pane = Track_Pane(window_height, window_width, window_height - 1, window_width, 0, 0, player_config["SCROLL-START"], self.stdscr)
        pane.refresh()
        pane.activate()
        self.panes.append(tab)

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
        
    def move_up(self):
        pass

    def move_down(self):
        pass

    def move_left(self):
        pass

    def move_right(self):
        pass
