#!/usr/bin/python3

import sys,os

from curses_elements import *
from database import *
from config import *

class Tab:
    def __init__(self, config_type, config_attr, stdscr, database, status_bar):
        self.panes = []
        self.pane_titles = []
        self.stdscr = stdscr
        self.isActive = False
        self.attr_keys = [] #GENRE, ALBUM, PERFORMER, TRACKS (Given)
        self.attr_values = [] #List of genres, List of albums, List of performers, "EMPTY" (Generated)
        self.filtered_tracks = []
        self.main_filter = [] #Main filter for the tab
        self.exclude_filter = []
        self.current_pane = 0
        self.database = database
        self.scrll_start = ui_config['SCRLL-TH']
        self.window_dims = [None, None]
        self.status_bar = status_bar
        self.do_not_overwrite = False
        self.selected_tracks = []
        self.in_add_to_playlist_mode = False

        self.height_offset = 2

        if config_type == "SINGLE":
            self.create_single_pane(config_attr)
        elif config_type == "4-PANE":
            self.create_4_pane(config_attr)
        elif config_type == "3-PANE":
            self.create_3_pane(config_attr)
        elif config_type == "2-PANE":
            self.create_2_pane(config_attr)
        elif config_type == "PLAYLIST":
            self.create_playlist_tab(config_attr)
        else:
            raise ValueError("Invalid config type")

    def add_to_playlist_pane(self):
        self.temp_vars = [self.attr_keys, self.attr_values, self.main_filter, self.exclude_filter, self.pane_titles]
        self.temp_panes = self.panes
        self.attr_keys = ["PLAYLIST"]
        self.attr_values = ["Empty"]
        self.main_filter = ["PLAYLISTS", None]
        self.exclude_filter = [None, None]
        self.pane_titles = ["Playlist"]

        self.filtered_tracks = self.database.get_all_tracks_with("PLAYLISTS", None, None, None)

        pane = List_Pane(self.window_dims[0], self.window_dims[1], #main window dims
                self.window_dims[0] - self.height_offset, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                self.scrll_start, self.stdscr, self.pane_titles[0])

        self.in_add_to_playlist_mode = True

        pane.selectedpos = 0
        pane.activate()
        self.panes = [pane]
        self.refresh_panes()
        self.populate_lists()
        #self.reset_tab()

    def add_to_playlist(self):
        if self.in_add_to_playlist_mode:
            selected_file = self.attr_values[0][self.panes[0].selectedpos] + ".m3u"
            with open(playlists_dir + "/" + selected_file, 'a') as f:
                for path in self.selected_tracks:
                    f.write(path)
                    f.write('\n')
            
            self.attr_keys, self.attr_values, self.main_filter, self.exclude_filter, self.pane_titles = self.temp_vars
            self.panes = self.temp_panes
            self.refresh_panes()

            new_tracks = self.database.get_all_tracks_with("PATH", self.selected_tracks, None, None).copy()
            for track in new_tracks:
                track["PLAYLIST"] = selected_file[:-4]
                self.database.playlists.playlist_dict_list.append(track.copy())

            del new_tracks

            self.in_add_to_playlist_mode = False

    def create_2_pane(self, config_attr):
        self.window_dims[0], self.window_dims[1], self.main_filter, self.exclude_filter, self.attr_keys, self.pane_titles = config_attr

        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1],
                self.exclude_filter[0], self.exclude_filter[1])

        pane1 = List_Pane(self.window_dims[0], self.window_dims[1], #main window dims
                self.window_dims[0] - self.height_offset, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                self.scrll_start, self.stdscr, self.pane_titles[0])

        pane2 = Track_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - 1, self.window_dims[1] - 29, 
                0, 29, 
                self.scrll_start, self.stdscr)

        pane1.activate()
        self.panes = [pane1, pane2]
        self.refresh_panes()
   
    def create_playlist_tab(self, config_attr):
        self.window_dims[0], self.window_dims[1], x, y, z, k = config_attr

        self.attr_keys.append("PLAYLIST")
        self.attr_values.append("Empty")
        self.main_filter = ["PLAYLISTS", None]
        self.exclude_filter = [None, None]
        self.pane_titles = ["Playlist", "TRACK"]
       
        self.filtered_tracks = self.database.get_all_tracks_with("PLAYLISTS", None, None, None)

        pane1 = List_Pane(self.window_dims[0], self.window_dims[1], #main window dims
                self.window_dims[0] - self.height_offset, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                self.scrll_start, self.stdscr, self.pane_titles[0])

        pane2 = Track_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - self.height_offset, self.window_dims[1] - 29, 
                0, 29, 
                self.scrll_start, self.stdscr)

        pane1.activate()
        self.panes = [pane1, pane2]
        self.refresh_panes()

    def create_4_pane(self, config_attr):
        self.window_dims[0], self.window_dims[1], self.main_filter, self.exclude_filter, self.attr_keys, self.pane_titles = config_attr

        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1],
                self.exclude_filter[0], self.exclude_filter[1])

        pane1 = List_Pane(self.window_dims[0], self.window_dims[1], #main window dims
                self.window_dims[0] - self.height_offset, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                self.scrll_start, self.stdscr, self.pane_titles[0])

        pane2 = List_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - self.height_offset, 60, 
                0, 29, 
                self.scrll_start, self.stdscr, self.pane_titles[1])

        pane3 = List_Pane(self.window_dims[0], self.window_dims[1], 
                9, self.window_dims[1] - 88, 
                0, 88, 
                self.scrll_start, self.stdscr, self.pane_titles[2])

        pane4 = Track_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - 8 - self.height_offset, self.window_dims[1] - 88, 
                8, 88, 
                self.scrll_start, self.stdscr)

        pane1.activate()
        self.panes = [pane1, pane2, pane3, pane4]
        self.refresh_panes()

    def create_3_pane(self, config_attr):
        self.window_dims[0], self.window_dims[1], self.main_filter, self.exclude_filter, self.attr_keys, self.pane_titles = config_attr

        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1],
                self.exclude_filter[0], self.exclude_filter[1])

        pane1 = List_Pane(self.window_dims[0], self.window_dims[1], #main window dims
                self.window_dims[0] - self.height_offset, 30, #height and width of pane
                0, 0, #y and x position of top left corner of pane
                self.scrll_start, self.stdscr, self.pane_titles[0])

        pane2 = List_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - self.height_offset, 60, 
                0, 29, 
                self.scrll_start, self.stdscr, self.pane_titles[1])

        pane3 = Track_Pane(self.window_dims[0], self.window_dims[1], 
                self.window_dims[0] - self.height_offset, self.window_dims[1] - 88, 
                0, 88, 
                self.scrll_start, self.stdscr)

        pane1.activate()
        self.panes = [pane1, pane2, pane3]
        self.refresh_panes()

    def create_single_pane(self, config_attr):
        self.window_dims[0], self.window_dims[1], self.main_filter, self.exclude_filter = [x for x in config_attr if x is not None]
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1], 
                self.exclude_filter[0], self.exclude_filter[1])

        self.attr_keys.append("TRACK")
        self.attr_values.append("Empty")
        pane = Track_Pane(self.window_dims[0], self.window_dims[1], self.window_dims[0] - self.height_offset, self.window_dims[1], 0, 0, self.scrll_start, self.stdscr)
        pane.refresh()
        pane.activate()
        self.panes.append(pane)

    def populate_lists(self):
        #this func must be run at least once in the beginning
        self.load_all_tracks()
        attr_values_tmp = []
        for key, pane in zip(self.attr_keys, self.panes):
            if not key == "TRACK" and not pane.selectedpos == None:
                tmp_list = get_unique_attributes(self.filtered_tracks, key)
                attr_values_tmp.append(tmp_list)
                self.filtered_tracks = get_tracks_with(self.filtered_tracks, key, [tmp_list[pane.selectedpos]])
            if not key == "TRACK" and pane.selectedpos == None:
                tmp_list = get_unique_attributes(self.filtered_tracks, key)
                attr_values_tmp.append(tmp_list)

        attr_values_tmp.append("Empty") #insert empty string in last entry for tracks in next loop
        self.attr_values = attr_values_tmp

    def render_all_panes(self, full_render=False):
        if self.isActive:
            if full_render:
                self.populate_lists()

            for pane, lst in zip(self.panes, self.attr_values):
                if pane.is_track_pane():
                    pane.render(self.filtered_tracks, self.selected_tracks)
                else:
                    pane.render(lst)

    def activate_tab(self):
        self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1],
                self.exclude_filter[0], self.exclude_filter[1])
        self.isActive = True

    def deactivate_tab(self):
        self.isActive = False
        del self.filtered_tracks

    def load_all_tracks(self):
        if self.isActive and not self.do_not_overwrite:
            self.filtered_tracks = self.database.get_all_tracks_with(self.main_filter[0], self.main_filter[1], self.exclude_filter[0], self.exclude_filter[1])

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

    def skip_down_pane(self):
        if self.isActive:
            for pane, l in zip(self.panes, self.attr_values):
                if not pane.is_track_pane():
                    for i in range(0, 10):
                        self.move_down()
                        self.render_all_panes(False)
                else:
                    for i in range(0, 10):
                        self.move_down()
                        self.render_all_panes(False)

    def skip_up_pane(self):
        if self.isActive:
            for pane in self.panes:
                for i in range(0, 10):
                    self.move_up()
                    self.render_all_panes(False)

    def move_left(self):
        if not self.current_pane == 0 and self.isActive and not self.do_not_overwrite:
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
    
    def jump_to_track_pane(self):
        if self.isActive:
            self.panes[self.current_pane].deactivate()
            self.current_pane = len(self.panes) - 1
            self.panes[len(self.panes) - 1].activate()

    def refresh_panes(self):
        if self.isActive:
            for pane in self.panes:
                pane.refresh()

    def clear_panes(self):
        for pane in self.panes:
            pane.clear()
     
    def reset_tab(self):
        if self.isActive:
            self.do_not_overwrite = False
            self.load_all_tracks()
            self.selected_tracks = []
            self.render_all_panes(True)
            self.refresh_panes()

    def select_track(self):
        if self.isActive:
            if self.panes[self.current_pane].is_track_pane():
                path = self.filtered_tracks[self.panes[self.current_pane].selectedpos]["PATH"]
                if path in self.selected_tracks:
                    self.selected_tracks.remove(path)
                    self.move_down()
                else:
                    self.selected_tracks.append(path)
                    self.move_down()
            else:
                self.selected_tracks += [track["PATH"] for track in self.filtered_tracks]

    def remove_tracks(self):
        if self.isActive:
            curses.cbreak()
            k = 100
            self.status_bar.set_bar_string("Are you sure? (y/n)")
            self.status_bar.render_bar()
            k = self.stdscr.getch()
            if k == ord('y'):
                self.database.delete_tracks_from_database(self.selected_tracks)

            curses.halfdelay(15)
            self.status_bar.set_bar_string("DEFAULT")
            self.status_bar.render_bar()

    def search_mode(self):
        if self.isActive:
            curses.cbreak()
            k = 100
            self.status_bar.set_bar_string("find: ")
            self.status_bar.render_bar()
            self.jump_to_track_pane()
            while (k != 27):
                self.render_all_panes(False)
                self.refresh_panes()
                k = self.stdscr.getch()
                if k == ord('\n'):
                    self.do_not_overwrite = True
                    #Remember at this point, current pane is the track pane
                    self.panes[self.current_pane].clear() #to ensure the selected track is within the bounds of the found tracks
                    for pane in self.panes:
                        if not pane.is_track_pane() and pane.can_show_position:
                            pane.reset_pos()
                    break
                elif k != ord('ć'):
                    self.status_bar.set_bar_string(self.status_bar.get_bar_string() + str(chr(k)))
                elif len(self.status_bar.get_bar_string()) > 6:
                    self.status_bar.set_bar_string(self.status_bar.get_bar_string()[:-1])
                    self.load_all_tracks()
                
                self.status_bar.render_bar()
                self.filtered_tracks = get_tracks_with(self.filtered_tracks, "TITLE", [self.status_bar.get_bar_string()[6:]])

            curses.halfdelay(15)
            self.status_bar.render_bar()

    def play_track(self):
        if self.isActive:
            client = start_mpd_client()

            subprocess.call(["mpc", "clear"], stdout=subprocess.PIPE)
            try:
                for track in self.filtered_tracks:
                    #subprocess.call(["mpc", "add", track["PATH"]], stdout=subprocess.PIPE)
                    client.add(track["PATH"])

                subprocess.call(["mpc", "play", 
                    str(self.panes[len(self.panes) - 1].selectedpos + 1)], stdout=subprocess.PIPE)
            except CommandError as e:
                height, width = self.stdscr.getmaxyx()
                self.status_bar.set_bar_string("MPD Error: " + str(e))


            stop_mpd_client(client)

    def toggle_random(self):
        if self.isActive:
            client = start_mpd_client()
            client.random(int(not bool(int(client.status()["random"]))))
            stop_mpd_client(client)
