#!/usr/bin/python3

import sys,os
import curses
from pathlib import Path
import taglib
from subprocess import call
import subprocess
import time
from multiprocessing import Process
import re
import datetime
from player_elements import *

tracktime = " "
debug_list = []

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s
    
def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s[0][2]) ]

def sorted_nicely_3d(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

def sorted_nicely( data ):
    return sorted(data, key=lambda item: (int(item.partition(' ')[0])
                               if item[0].isdigit() else float('inf'), item))

def update_database(directory_str):
    pathlist = Path(directory_str).glob('**/*.flac')

    cutoff = len(directory_str) #where to start to remove first part of path not needed by mpc

    initial_tracks = []

    for path in pathlist:
        path_in_str = str(path)
        song = taglib.File(path)

        title = str(song.tags["TITLE"])
        title = title[2:]
        title = title[:-2]

        cutpath = path_in_str
        cutpath = cutpath[cutoff + 1:] #cut off part of directory

        album = str(song.tags["ALBUM"])
        album = album[2:]
        album = album[:-2]

        tracknum = str(song.tags["TRACKNUMBER"])
        tracknum = tracknum[2:]
        tracknum = tracknum[:-2]
        tracknum = int(tracknum)

        tracklength = song.length

        genre = str(song.tags["GENRE"])
        genre = genre[2:]
        genre = genre[:-2]

        performer = str(song.tags["PERFORMER"])
        performer = performer[2:]
        performer = performer[:-2]

        temp_list = []
        temp_list.append(title)
        temp_list.append(cutpath)
        temp_list.append(album)
        temp_list.append(tracknum)
        temp_list.append(tracklength)
        temp_list.append(genre)
        temp_list.append(performer)

        initial_tracks.append(temp_list)

    tracks_grouped_album = initial_tracks.copy()            #currently assuming tracks are already grouped by album
    #tracks_grouped_album = []                               #groups the tracks in sections by album, not in order
    #for album_track in initial_tracks:
    #    current_album = album_track[2]
    #    tracks_grouped_album.append(album_track)
    #    #print(album_track[0])
    #    for check_track in initial_tracks:
    #        #print(check_track[0])
    #        if current_album == check_track[2]:
    #            tracks_grouped_album.append(check_track)
    #            initial_tracks.remove(check_track)
    #            #print(check_track[0])

    del initial_tracks[:]

    album_check = tracks_grouped_album[0][2]
    sorted_tracks_inalbum = []
    album = []
    for track in tracks_grouped_album:  #sorts tracks by tracknumber in albums, putting them into a 3d list album->track->metadata
        if track[2] == album_check:
            album.append(track)
        else:
            album = sorted(album,key=lambda x: x[3])
            sorted_tracks_inalbum.append(album)
            album_check = track[2]
            album = []
            album.append(track)

    album = sorted(album,key=lambda x: x[3])
    sorted_tracks_inalbum.append(album)

    del tracks_grouped_album[:]

    sorted_nicely_3d(sorted_tracks_inalbum) #sorts the albums

    sorted_tracks = []
    for album in sorted_tracks_inalbum:
        for track in album:
            sorted_tracks.append(track)

    file = open("database", "w")
    for track in sorted_tracks:
        for metadata in track:
            file.write(str(metadata) + "\n")

    file.close()

    #mode 2 database prep
    #find unique genres
    unique_genres = []
    tmp_genre_list = []
    albums_by_genre = []

    list_size = len(sorted_tracks_inalbum)
    i = 0
    j = 0
    while list_size > 0:
        unique_genres.append(sorted_tracks_inalbum[i][0][5])
        album_check = sorted_tracks_inalbum[i][0][5]
        while j < list_size:
            if album_check == sorted_tracks_inalbum[j][0][5]:
                print(sorted_tracks_inalbum[j][0][5])
                tmp_genre_list.append(sorted_tracks_inalbum[j])
                sorted_tracks_inalbum.remove(sorted_tracks_inalbum[j])
                list_size = list_size - 1
                j = j - 1
            j = j + 1

        albums_by_genre.append(tmp_genre_list)
        tmp_genre_list = []
        j = 0

    #albums_by_genre.append(tmp_genre_list)

    file = open("database", "a")
    file.write("{END}\n")
    for genre in unique_genres:
        file.write(genre + "\n")

    file.write("{END}\n")

    for genre in albums_by_genre:
        for album in genre:
            file.write(album[0][2] + "\n")
            tmp_list = []
            for track in album:
                tmp_list.append(track[6])
            new_list = list(set(tmp_list))
            for performer in new_list:
                file.write(performer + "\n")
            file.write("{ENDWORK}\n")
        file.write("{END}\n")
    file.close()

    print(len(albums_by_genre))

def draw_menu(stdscr):
    keydict = {
        "DOWN":     ord('j'),
        "UP":       ord('k'),
        "LEFT":     ord('h'),
        "RIGHT":    ord('l'),
        "PLAY":     ord('n'),
        "SEARCH":   ord('s'),
        "SEEKF":    ord('f'),
        "SEEKB":    ord('r'),
        "TAB1":     ord('1'),
        "TAB2":     ord('2'),
        "ESCAPE":   27,
        "QUIT":     ord('q')
    }

    k = 100
    curses.halfdelay(5)
    halfseconds = 1
    firstTime = True
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(False)
    stdscr.nodelay(0)
    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, 124)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, 124)
    curses.init_pair(6, 124, curses.COLOR_BLACK)


    height, width = stdscr.getmaxyx()

    find_mode = False
    has_escaped_find = True
    #initialize in mode 1, display alltracks
    tab = 1

    #tab or "mode" 1 variables
    alltracks_unsorted = []          #initialize array for all tracks mode
    alltracks = []
    tmp_alltracks = []      #holding alltracks during find mode

    #populate alltracks array as 2d arrray
    tmpList = []
    index = 0
    inAlltracks = True
    inGenres = False
    inGenreAlbums = False
    inPerformer = False
    genre_list = []
    album_genre_list = []
    performer_list = []
    with open('database', 'r') as ins:
        tmp_list = []
        for line in ins:
            if inAlltracks:
                if str(line) == "{END}\n":
                    inGenres = True
                    inAlltracks = False
                elif index < 6:
                    tmpList.append(line.rstrip('\n'))
                    index = index + 1 
                elif index == 6:
                    tmpList.append(line.rstrip('\n'))
                    alltracks_unsorted.append(tmpList)
                    tmpList = []
                    index = 0
            elif inGenres:
                if str(line) != "{END}\n":
                    genre_list.append(line.rstrip('\n'))
                else:
                    inGenres = False
                    inGenreAlbums = True
            elif inGenreAlbums:
                if str(line) != "{END}\n":
                    if inPerformer:
                        if str(line) != "{ENDWORK}\n":
                            performer_list.append(line.rstrip('\n'))
                        else:
                            tmp_list.append(performer_list)
                            performer_list = []
                            inPerformer = False
                    else:
                        tmp_list.append(line.rstrip('\n'))
                        inPerformer = True
                else:
                    album_genre_list.append(tmp_list)
                    tmp_list = []
    alltracks = alltracks_unsorted
    global debug_list
    debug_list = album_genre_list.copy()

    tab1_x = 0; tab1_y = 0
    tab1_height = height - 1; tab1_width = width
    tab1_pane = Track_Pane(height, width, tab1_height, tab1_width, tab1_y, tab1_x, 8, stdscr)

    tab1_pane.refresh()
    tab1_pane.activate()

    #tab or "mode" 2 variables
    listpos = 0

    new_x = 0; new_y = 0
    new_height = height - 1; new_width = 30
    tab2_genrepane = List_Pane(height, width, new_height, new_width, new_y, new_x, 8, stdscr, "Genre")

    x_2 = 29; y_2 = 0
    height_2 = height - 1; width_2 = 60;
    tab2_workpane = List_Pane(height, width, height_2, width_2, y_2, x_2, 8, stdscr, "Work")

    x_3 = 88; y_3 = 0
    height_3 = 9; width_3 = width - (x_3);
    tab2_performerpane = List_Pane(height, width, height_3, width_3, y_3, x_3, 8, stdscr, "Performer")

    x_4 = 88; y_4 = 8
    height_4 = height - 9; width_4 = width - (x_3);

    tab2_trackpane = Track_Pane(height, width, height_4, width_4, y_4, x_4, 8, stdscr)

    tab2_genrepane.refresh()
    tab2_genrepane.activate()
    tab2_workpane.refresh()
    tab2_trackpane.refresh()
    tab2_performerpane.refresh()

    listarray = genre_list
    listarray.append(" ") #in order not to highlight borders when list hits bottom

    # Loop where k is the last character pressed
    while (k != keydict["QUIT"]):
        valid_input = [ord('j'), ord('k'), ord('l'), ord('h'), ord('p'), ord('f'), ord('r'), ord('n'), ord('1'), ord('2'), ord('s'), 27]
        # Initialization
        #stdscr.clear()
        height, width = stdscr.getmaxyx()
        if find_mode == False:
            if k == ord('j') or k == curses.KEY_SF:
                if tab == 1:
                    tab1_pane.move_down_one(len(alltracks))
                if tab == 2:
                    if listpos == 0:
                        tab2_genrepane.move_down_one(len(genre_list) - 1)
                    if listpos == 1:
                        tab2_workpane.move_down_one(len(album_genre_list[tab2_genrepane.selectedpos]) / 2)
                    if listpos == 2:
                        tab2_performerpane.move_down_one(len(performer_listarray))
                    if listpos == 3:
                        tab2_trackpane.move_down_one(len(alltracks))
            elif k == ord('k') or k == curses.KEY_SR:
                if tab == 1:
                    tab1_pane.move_up_one()
                if tab == 2:
                    if listpos == 0:
                        tab2_genrepane.move_up_one()
                    if listpos == 1:
                        tab2_workpane.move_up_one()
                    if listpos == 2:
                        tab2_performerpane.move_up_one()
                    if listpos == 3:
                        tab2_trackpane.move_up_one()
            elif k == ord('l'):
                if tab == 2 and listpos < 3:
                    listpos = listpos + 1
                    if listpos == 0:
                        tab2_genrepane.activate()
                    if listpos == 1:
                        tab2_workpane.activate()
                    if listpos == 2:
                        tab2_performerpane.activate()
                    if listpos == 3:
                        tab2_trackpane.activate()
                if listpos == 2:
                    tmp_alltracks = alltracks
            elif k == ord('h'):
                if tab == 2:
                    if listpos == 1:
                        tab2_workpane.disactivate()
                        tab2_workpane.clear()
                    if listpos == 2:
                        alltracks = tmp_alltracks
                        tab2_performerpane.disactivate()
                        tab2_performerpane.clear()
                    if listpos == 3:
                        tab2_trackpane.disactivate()
                        tab2_trackpane.clear()
                    if listpos != 0:
                        listpos = listpos - 1
            elif k == curses.KEY_RESIZE:
                stdscr.erase()
            elif k == ord('1'):
                tab = 1
            elif k == ord('2'):
                tab = 2
                stdscr.erase()
            elif k == ord('n'):
                if tab == 1:
                    path = alltracks[tab1_pane.trackpos][1]
                    subprocess.call(["mpc", "clear"], stdout=subprocess.PIPE)
                    subprocess.call(["mpc", "add", path], stdout=subprocess.PIPE)
                    subprocess.call(["mpc", "play"], stdout=subprocess.PIPE)
                if tab == 2:
                    subprocess.call(["mpc", "clear"], stdout=subprocess.PIPE)
                    for track in alltracks:
                        path = track[1]
                        subprocess.call(["mpc", "add", path], stdout=subprocess.PIPE)
                    subprocess.call(["mpc", "play", str(tab2_trackpane.trackpos + 1)], stdout=subprocess.PIPE)
            elif k == ord('p'):
                subprocess.call(["mpc", "toggle"], stdout=subprocess.PIPE)
            elif k == ord('s'):
                k = ord(' ')
                statusbarstr = "find:"
                find_mode = True
                tab1_pane.clear()
                if has_escaped_find:
                    tmp_alltracks = alltracks
                has_escaped_find = False
            elif k == ord('f'):
                subprocess.call(["mpc", "seek", "+00:00:5"], stdout=subprocess.PIPE)
            elif k == ord('r'):
                subprocess.call(["mpc", "seek", "-00:00:5"], stdout=subprocess.PIPE)
            elif k == 27:
                alltracks = tmp_alltracks
        elif k == ord('\n'):
            statusbarstr = ""
            k = 0
            find_mode = False
        elif k == 27:
            alltracks = tmp_alltracks
            find_mode = False
            has_escaped_find = True
        elif k == ord('ć'):
            if len(statusbarstr) != 6:
                statusbarstr = statusbarstr[:-1]
        # Declaration of strings
        #global tracktime
        if find_mode == False:
            
            statusbarstr = "{}, {} | Width: {} | {}/{}".format(width, height, width, "Testing", str(len(alltracks)))
            songtime = subprocess.run("mpc status | grep '%)' | awk '{ print $3 }'", stdout=subprocess.PIPE, shell=True)
            tmpstr = str(songtime.stdout)
            tmpstr = tmpstr[2:]
            tmpstr = tmpstr[:-3]
            statusbarstr = statusbarstr + " " + tmpstr

        elif k != curses.ERR:
            if k != ord('ć'):
                statusbarstr = statusbarstr + str(chr(k))
            string_match = statusbarstr[6:]
            w, h = 2, 1
            alltracks = tmp_alltracks
            tmp_list = []
            if string_match != "":
                for track in alltracks:
                    test_string = track[0]
                    if string_match in test_string:
                        tmp_list.append(track)
                alltracks = tmp_list
                tab1_pane.refresh()

        if tab == 2 and ((k in valid_input) or (halfseconds % 10 == 0)):
            halfseconds = 1
            secondary_listarray = []
            performer_listarray = []
            performer_listarray_tmp = []
            onAlbum = True
            for album in album_genre_list[tab2_genrepane.selectedpos]:
                if onAlbum:
                    secondary_listarray.append(album)
                    onAlbum = False
                else:
                    performer_listarray_tmp.append(album)
                    onAlbum = True

            performer_listarray = performer_listarray_tmp[tab2_workpane.selectedpos]
            list3size = len(performer_listarray)

            if listpos == 2:
                it = 0
                tmp_list = []
                alltracks = tmp_alltracks
                genre_string = listarray[tab2_genrepane.selectedpos]
                album_string = secondary_listarray[tab2_workpane.selectedpos]
                performer_string = performer_listarray[tab2_performerpane.selectedpos]
                for track in alltracks:
                    if str(track[5]) == genre_string and str(track[2]) == album_string and str(track[6]) == performer_string:
                        tmp_list.append(track)
                alltracks = tmp_list
            
            tab2_genrepane.render(listarray)
            tab2_workpane.render(secondary_listarray)
            tab2_performerpane.render(performer_listarray)
            tab2_trackpane.render(alltracks)

        if tab == 1 and (k in valid_input) or firstTime or (find_mode and (k != curses.ERR)):
            firstTime = False
           
            tab1_pane.render(alltracks)

        ## Rendering some text
        # Render status bar
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))

        # Refresh the screen
        if tab == 2 and k in valid_input:
            tab2_genrepane.refresh()
            tab2_workpane.pane.refresh()
            tab2_performerpane.refresh()
            stdscr.attron(curses.color_pair(6))
            
        stdscr.attroff(curses.color_pair(5))

        if tab == 2:
            tab2_trackpane.refresh()
        if tab == 1:
            tab1_pane.refresh()
        
        halfseconds += 1
        # Wait for next input
        k = stdscr.getch()
        #time.sleep(.01)

def time_loop():
    while 1:
        songtime = subprocess.run("mpc status | grep '%)' | awk '{ print $2 }'", stdout=subprocess.PIPE, shell=True)
        tmpstr = str(songtime.stdout)
        tmpstr = tmpstr[1:]
        tmpstr = tmpstr[:-3]
        global tracktime
        tracktime = tmpstr
        time.sleep(1)

def main():
    #update_database("/home/guillermo/bach/Music/Bach/FLAC")
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(draw_menu)
    #Process(target=time_loop).start()
    #print(debug_list)

if __name__ == "__main__":
    main()

