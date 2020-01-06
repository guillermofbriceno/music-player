import sys,os
import curses
import datetime
import time
import subprocess
import logging
from subprocess import call
from mpd import MPDClient, MPDError, CommandError

def start_mpd_client():
    client = MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)
    return client

def stop_mpd_client(client):
    client.close()
    client.disconnect()

def mpd_get_current_playing():
    client = start_mpd_client()
    song = client.currentsong()
    stop_mpd_client(client)
    return song

def mpd_get_status():
    client = start_mpd_client()
    status = client.status()
    stop_mpd_client(client)
    return status

def seconds_to_minutes(seconds):
    m, s = divmod(seconds, 60)
    return '{:02d}:{:02d}'.format(m, s)

def norm(size, string):
    return " " * (size - len(string)) + string

class Seek_Bar:
    def __init__(self, stdscr, ypos, width):
        self.stdscr = stdscr
        self.ypos = ypos
        self.width = width

    def draw(self):
        elapsed_time, duration = self.get_track_times()
        characters_elapsed =  int(round((self.width * elapsed_time) / duration))

        self.stdscr.attron(curses.color_pair(8))
        self.stdscr.addstr(self.ypos - 1, 0, " " * characters_elapsed)
        self.stdscr.attroff(curses.color_pair(8))
        self.stdscr.attron(curses.color_pair(2))
        if not self.width == characters_elapsed:
            self.stdscr.addstr(self.ypos - 1, characters_elapsed, " " * (self.width - characters_elapsed))
        self.stdscr.attroff(curses.color_pair(2))

    def seek(self, mouse_event):
        _, mousex, mousey, _, _ = mouse_event

        if mousey == self.ypos - 1:
            elapsed_time, duration = self.get_track_times()
            seconds_to_seek = (duration * mousex) / self.width
            client = start_mpd_client()
            client.seekcur(seconds_to_seek)

    def get_track_times(self):
        client = start_mpd_client()
        status = client.status()

        if "elapsed" in status:
            elapsed_time = float(status["elapsed"])
            duration = float(status["duration"])
            stop_mpd_client(client)
            return [elapsed_time, duration]
        else:
            stop_mpd_client(client)
            return [0, 1]

class Status_Bar:
    def __init__(self, first_string, stdscr, ypos, width):
        self.bar_string = ""
        self.stdscr = stdscr
        self.ypos = ypos
        self.width = width
        self.set_bar_string(first_string)
        self.number_of_tabs = 1
        self.current_tab = 1
    
    def set_bar_string(self, string):
        if string == "DEFAULT":
            track = mpd_get_current_playing()
            self.bar_string = track.get("title") or "No Track"
        else:
            self.bar_string = string
    
    def render_bar(self):
        char_dict = {
                'play' : '▶',
                'pause': '⏸',
                'stop' : '⏹'
                }

        self.stdscr.attron(curses.color_pair(5))
        status = mpd_get_status()
        state = norm(2, char_dict[status["state"]])
        
        if "elapsed" in status:
            elapsed_time = seconds_to_minutes(round(float(status["elapsed"])))
            duration = seconds_to_minutes(round(float(status["duration"])))
            time = elapsed_time + "/" + duration
        else:
            time = " "

        audio = status.get("audio") or " "
        bitrate = status.get("bitrate") or " "
        random = " " if status.get("random") is '0' else "  |  shuffle  "
            
        playlistlength = norm(4, status["playlistlength"])
        info_string = norm(20, ''.join(["[", audio, " @ ", bitrate, "kbps", "]"]))
        right_aligned =  ''.join([time, " | ", playlistlength, " Tracks Queued  | ", state, random, " | ", self.create_tab_string()])

        if (len(info_string) + len(self.bar_string) + 10) >= (self.width - len(right_aligned)):
            left_aligned = self.bar_string[:-((len(info_string) + len(self.bar_string)) - (self.width - len(right_aligned)) + 10)]
            left_aligned += ".. |  " + info_string
        else:
            left_aligned = self.bar_string + "  |  " + info_string

        full_string = ''.join([left_aligned, " " * (self.width - (len(right_aligned) + len(left_aligned)) - 3), right_aligned])

        self.stdscr.addstr(self.ypos - 1, 0, full_string)
        self.stdscr.addstr(self.ypos - 1, len(full_string), " " * (self.width - len(full_string) - 1))

        self.stdscr.attroff(curses.color_pair(5))

    def get_bar_string(self):
        return self.bar_string
    
    def set_number_of_tabs(self, num):
        self.number_of_tabs = num

    def set_current_tab(self, num):
        self.current_tab = num

    def create_tab_string(self):
        string = ""
        for tab in range(1, self.number_of_tabs + 1):
            if tab == self.current_tab:
                string += " [" + str(tab) + "] "
            else:
                string += "  " + str(tab) + "  "

        return string

class List_Pane:
    def __init__(self, global_height, global_width, pane_height, pane_width, ypos, xpos, startscroll, stdscr, title):
        self.global_width = global_width
        self.global_height = global_height
        self.pane_width = pane_width
        self.pane_height = pane_height
        self.startscroll = startscroll
        self.xpos = xpos
        self.ypos = ypos
        self.can_show_position = False
        self.isActive = False
        self.stdscr = stdscr
        self.title = title
        
        self.selectedpos = None
        self.vertpos = 0
        self.scrolloffset = 0

        #create window
        self.pane = curses.newwin(pane_height, pane_width, ypos, xpos)
        self.pane.refresh()

    def render(self, string_list):
        i = 0
        string_list.append(" ")
        self.pane.erase()
        #scrolling logic, scrolling down. Scroll point set after height - last number should be 1 minus that
        if (self.vertpos == (self.global_height - self.startscroll)) and (self.selectedpos < (len(string_list) - (self.startscroll - 3))):
            self.scrolloffset += 1
            self.vertpos -= 1

        #scrolling logic, scrolling up
        if self.scrolloffset > 0 and self.vertpos == (self.startscroll - 2):
            self.scrolloffset -= 1
            self.vertpos += 1

        current_playing_song = mpd_get_current_playing()


        for string in string_list:
            is_string_current_playing = string in current_playing_song.values()
            string = str(string_list[i + self.scrolloffset])
            if is_string_current_playing:
                string = "▶ " + string

            if len(string) + 2 >= self.pane_width:
                string = string[:-(len(string) - self.pane_width + 4)]
                string = string + ".."
            if self.vertpos == i and self.can_show_position:
                self.pane.attron(curses.color_pair(3))
                self.pane.addstr(i + 1, len(string), " " * (self.pane_width - len(string) - 1))
            else:
                if not is_string_current_playing:
                    self.pane.attron(curses.color_pair(2))
                    self.pane.addstr(i + 1, len(string), " " * (self.pane_width - len(string) - 1))
                else:
                    self.pane.attron(curses.color_pair(6))
                    self.pane.addstr(i + 1, len(string), " " * (self.pane_width - len(string) - 1))

            self.pane.addstr(i + 1, 1, string)
            i += 1
            
            if i == self.pane_height - 1:
                break
            
        string_list.pop()
        
        self.render_borders()

    def activate(self):
        self.isActive = True
        if not self.can_show_position:
            self.selectedpos = 0
        self.can_show_position = True
            
    def deactivate(self):
        self.isActive = False

    def keep_showing_position(self):
        self.can_show_position = True

    def stop_showing_position(self):
        self.can_show_position = False

    def clear(self):
        self.vertpos = 0
        self.selectedpos = None
        self.scrolloffset = 0

    def reset_pos(self):
        self.vertpos = 0
        self.selectedpos = 0
        self.scrolloffset = 0

    def refresh(self):
        self.pane.refresh()
        self.render_borders()

    def update_dims(self, height, width):
        self.global_height = height
        self.global_width = width

    def move_down_one(self, listlength):
        if self.isActive and (self.selectedpos < listlength - 1):
            self.vertpos += 1
            self.selectedpos += 1

    def move_up_one(self):
        if self.isActive and (self.selectedpos != 0):
            self.vertpos -= 1
            self.selectedpos -= 1

    def set_list_length(self, listlength):
        self.listlength = listlength

    def render_borders(self):
        self.stdscr.attron(curses.color_pair(6))

        self.stdscr.addstr(self.ypos, self.xpos + len(self.title), "─" * (self.pane_width - 1 - len(self.title)), curses.color_pair(2))

        if self.xpos > 0:
            self.stdscr.addstr(self.ypos, self.xpos, "┬───", curses.color_pair(2))
            self.pane.border(0,0,0,0,curses.ACS_TTEE,0,curses.ACS_BTEE,0)
        else:
            self.pane.border(0,0,0,0,0,curses.ACS_TTEE,0,curses.ACS_BTEE)

        self.stdscr.addstr(self.ypos, self.xpos + 4, self.title)

        self.stdscr.attroff(curses.color_pair(5))

    def is_track_pane(self):
        return False

class Track_Pane(List_Pane):
    def __init__(self, global_height, global_width, pane_height, pane_width, ypos, xpos, startscroll, stdscr):
        """Initializes a track pane.
        
        Args:
            global_height (int): The window height
            global_width (int): The window width
            pane_height (int): Desired pane height
            pane_width (int): Desired pane width
            ypos (int): Desired y position
            xpos (int): Desired x position
            startscroll (int): Threshold for when the list begins to scroll
            stdcr (curses window): Standard curses window

        """
        self.global_width = global_width
        self.global_height = global_height
        self.pane_width = pane_width
        self.pane_height = pane_height
        self.startscroll = startscroll
        self.xpos = xpos
        self.ypos = ypos
        self.isActive = False
        self.can_show_position = False
        self.stdscr = stdscr
        self.selectedpos = 0
        self.vertpos = 0
        self.scrolloffset = 0
        self.current_playing_path = "" #unique to this class

        #create window
        self.pane = curses.newwin(pane_height, pane_width, ypos, xpos)
        self.pane.refresh()

    def render(self, track_dicts, selected_track_paths):
        empty_dict = {  "TITLE":" ",
                        "PATH": " ",
                        "TRACKNUMBER": " ",
                        "LENGTH": " "
        } #in order to not render bottom row track, causing borders
        track_dicts.append(empty_dict)
        i = 0
        self.pane.erase()

        if (self.vertpos == (self.pane_height - self.startscroll)) and (self.selectedpos < (len(track_dicts) - (self.startscroll - 2))):
            self.scrolloffset += 1
            self.vertpos -= 1

        if self.scrolloffset > 0 and self.vertpos == (self.startscroll - 2):
            self.scrolloffset -= 1
            self.vertpos += 1

        for track in track_dicts:
            title = track_dicts[i + self.scrolloffset]["TITLE"]
            trackpath = track_dicts[i + self.scrolloffset]["PATH"]
            tracknum = track_dicts[i + self.scrolloffset]["TRACKNUMBER"]
            tracklength = track_dicts[i + self.scrolloffset]["LENGTH"]

            trackIsNowPlaying = trackpath in self.current_playing_path

            if (i + self.scrolloffset) != (len(track_dicts) - 1):
                tracktime = str(datetime.timedelta(seconds=int(tracklength)))
            else:
                tracktime = " "

            if trackpath in selected_track_paths:
                space = (5 - len(tracknum)) * " "    
                if trackIsNowPlaying:
                    space = space[2:]
                    space += "▶ "
                space += "*"
            elif trackIsNowPlaying and len(trackpath) != 1:
                space = (2 - len(tracknum)) * " "    
                space += "▶ "
            else:
                space = (4 - len(tracknum)) * " "    

            title = tracknum + space + title

            if len(title) >= self.pane_width - 9:
                title = title[:-(len(title) - self.pane_width + 11)]
                title += ".."

            if self.vertpos == i and self.can_show_position:
                self.pane.attron(curses.color_pair(3))
                self.pane.addstr(i + 1, len(title), " " * (self.pane_width - len(title) - 8) + tracktime)
            elif trackpath in selected_track_paths:
                self.pane.attron(curses.color_pair(7))
                self.pane.addstr(i + 1, len(title), " " * (self.pane_width - len(title) - 8) + tracktime)
            else:
                if not trackIsNowPlaying:
                    self.pane.attron(curses.color_pair(2))
                    self.pane.addstr(i + 1, len(title), " " * (self.pane_width - len(title) - 8) + tracktime)
                else:
                    self.pane.attron(curses.color_pair(6))
                    self.pane.addstr(i + 1, len(title), " " * (self.pane_width - len(title) - 8) + tracktime)

            self.pane.addstr(i + 1, 1, title)
            self.pane.attroff(curses.color_pair(2))

            i += 1

            if i == self.pane_height - 2:
                break

        track_dicts.pop()
       
        self.render_borders()
        
    def activate(self):
        self.isActive = True
        self.can_show_position = True
    
    def clear(self):
        self.vertpos = 0
        self.selectedpos = 0
        self.scrolloffset = 0

    def refresh(self):
        self.pane.refresh()
        tmp = subprocess.run("mpc -f '%file%' | head -1", stdout=subprocess.PIPE, shell=True)
        self.current_playing_path = str(tmp.stdout.decode('utf-8'))

    def render_borders(self):
        self.pane.attron(curses.color_pair(2))
        if self.ypos > 0:
            self.pane.border(0,0,0,0,curses.ACS_LTEE,curses.ACS_RTEE,curses.ACS_BTEE,0)
        elif self.ypos == 0 and self.xpos == 0:
            self.pane.border(0,0,0,0,0,0,0,0)
        elif self.ypos == 0 and self.xpos > 0:
            self.stdscr.addstr(self.ypos, self.xpos, "┬", curses.color_pair(2))
            self.pane.border(0,0,0,0,curses.ACS_LTEE,0,curses.ACS_BTEE,0)


        self.stdscr.refresh()
        self.stdscr.attron(curses.color_pair(6))

        self.stdscr.addstr(self.ypos, self.xpos + 1, "#")
        self.stdscr.addstr(self.ypos, self.xpos + 2, "─" * 3, curses.color_pair(2))
        self.stdscr.addstr(self.ypos, self.xpos + 5, "Title")
        self.stdscr.addstr(self.ypos, self.xpos + 10, "─" * (self.pane_width - 15), curses.color_pair(2))
        self.stdscr.addstr(self.ypos, (self.xpos + self.pane_width) - 7, "Length")

        self.stdscr.attroff(curses.color_pair(5))

    def is_track_pane(self):
        return True



