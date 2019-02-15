#!/usr/bin/python3

import sys,os
import curses
import datetime
import time
import subprocess
from subprocess import call

def status_bar(string, stdscr, ypos, width):
    stdscr.attron(curses.color_pair(5))
    stdscr.addstr(ypos - 1, 0, string)
    stdscr.addstr(ypos - 1, len(string), " " * (width - len(string) - 1))
    stdscr.attroff(curses.color_pair(5))

class Track_Pane:
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
        self.trackpos = 0
        self.vertpos = 0
        self.scrolloffset = 0
        self.current_playing_path = ""

        #create window
        self.pane = curses.newwin(pane_height, pane_width, ypos, xpos)
        self.pane.refresh()

    def render(self, track_dicts):
        empty_dict = {  "TITLE":" ",
                        "PATH": " ",
                        "TRACKNUMBER": " ",
                        "LENGTH": " "
        } #in order to not render bottom row track, causing borders
        track_dicts.append(empty_dict)
        i = 0
        self.pane.erase()

        if (self.vertpos == (self.pane_height - self.startscroll)) and (self.trackpos < (len(track_dicts) - (self.startscroll - 2))):
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

            space = (4 - len(tracknum)) * " "    
            title = tracknum + space + title

            if len(title) >= self.pane_width - 9:
                title = title[:-(len(title) - self.pane_width + 11)]
                title += ".."

            if self.vertpos == i and self.can_show_position:
                self.pane.attron(curses.color_pair(3))
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
    
    def deactivate(self):
        self.isActive = False

    def keep_showing_position(self):
        self.can_show_position = True

    def stop_showing_position(self):
        self.can_show_position = False

    def clear(self):
        self.vertpos = 0
        self.trackpos = 0
        self.scrolloffset = 0

    def refresh(self):
        self.pane.refresh()
        tmp = subprocess.run("mpc -f '%file%' | head -1", stdout=subprocess.PIPE, shell=True)
        self.current_playing_path = str(tmp.stdout.decode('utf-8'))

    def update_dims(self, height, width):
        self.global_height = height
        self.global_width = width

    def move_down_one(self, listlength):
        if (self.trackpos != (listlength - 1)) and self.isActive:
            self.vertpos += 1
            self.trackpos += 1

    def move_up_one(self):
        if (self.trackpos != 0) and self.isActive:
            self.vertpos -= 1
            self.trackpos -= 1

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
        if (self.vertpos == (self.global_height - self.startscroll)) and (self.selectedpos < (len(string_list) - (self.startscroll - 2))):
            self.scrolloffset += 1
            self.vertpos -= 1

        #scrolling logic, scrolling up
        if self.scrolloffset > 0 and self.vertpos == (self.startscroll - 2):
            self.scrolloffset -= 1
            self.vertpos += 1

        for string in string_list:
            string = str(string_list[i + self.scrolloffset])

            if len(string) + 2 >= self.pane_width:
                string = string[:-(len(string) - self.pane_width + 4)]
                string = string + ".."
            if self.vertpos == i and self.can_show_position:
                self.pane.attron(curses.color_pair(3))
                self.pane.addstr(i + 1, len(string), " " * (self.pane_width - len(string) - 1))
            else:
                self.pane.attron(curses.color_pair(2))
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

