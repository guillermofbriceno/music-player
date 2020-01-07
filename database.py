import sys,os
from pathlib import Path
import taglib
import pickle
from fractions import Fraction
from functools import reduce
import re
from config import *
import logging
from mpd import MPDClient, MPDError, CommandError

def start_mpd_client():
    client = MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)
    return client
 
def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s
    
def alphanum_key(track):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)',  track["album"] + track["TRACKNUMBER"])]

def normal_sort(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)


def get_unique_attributes(dict_list, attr):
    """Return uniqified list of attributes/keys matching attr.
    Args:
        dict_list (list of dicts): The list of dictionaries to be searched.
        attr (str): Attribute/key being matched for.

    Returns:
        list: List of string attribute values."""

    seen = set()
    seen_add = seen.add
    tmp_list = []
    for x in dict_list:
        if attr in x:
            if type(x[attr]) is list:
                string = "+"
                x[attr] = string.join(x[attr])
            if not (x[attr] in seen or seen_add(x[attr])):
                tmp_list.append(x[attr])

    return tmp_list


def get_tracks_with(dict_list, attrkey, attrvalue):
        """Return list of tracks with specified attributes.
        Args:
            dict_list (list): List of track dictionaries.
            attrkey (str): The attribute key or type.
            attrvalue (list): The attribute(s) being matched for.

        Returns:
            list: List of track dictionaries."""

        return [track for track in dict_list 
                if attrkey in track.keys() 
                if any(val in track[attrkey] for val in attrvalue)]


def dump_database(database):
    database_name = db_dir[0][db_dir[0].rfind("/") + 1:] + "-db"
    db_file = open(install_dir + "/" + database_name, 'wb')
    pickle.dump(database, db_file)

def start_database(directory_strs, playlists_dir):
    database = Database(directory_strs)
    playlists = Playlists(playlists_dir, directory_strs, database)
    database.add_playlists(playlists)
    return database

def database_file_already_exists(file_name):
    """Check if database file exists in the running/database directory.
    Args:
        file_name (str): The name of the file in the running directory.
    Returns:
        bool: Whether or not the file was found"""
    return os.path.isfile(install_dir + "/" + file_name)

def cut_brackets(tag):
        string = str(tag)
        string = string[2:]
        string = string[:-2]
        return string

def create_track(path, dir_str):
    track = taglib.File(path)
    #Read the dict from taglib by removing the brackets from the values
    tmp_tagdict = {k: cut_brackets(tag) for k, tag in track.tags.items()}
    #Add length and path to the track dictionary. Absolute path cut MPC prep
    tmp_tagdict["PATH"] = str(path)[len(dir_str) + 1:]
    tmp_tagdict["LENGTH"] = track.length
    #Handle weird tracknumber cases for sorting methods
    tracknum_tmp = tmp_tagdict["TRACKNUMBER"]
    if '/' in tracknum_tmp:
        tmp_tagdict["TRACKNUMBER"] = tracknum_tmp[:-tracknum_tmp.rfind("/") - 1]
    elif tracknum_tmp.isdigit():
        pass
    else:
        tmp_tagdict["TRACKNUMBER"] = "0"

    return tmp_tagdict


class Database:
    """A representation of the entire music library.
    Args:
        directory_str (str): The directory of the music folder.
    """
    def __init__(self, directory_strs):
        self.dict_list = []
        self.directory_strs = directory_strs
        self.generate_database(directory_strs)
        self.sort_tracks("NORMAL")

    def generate_database(self, directory_strs):
        print("Generating database...\n")
        client = start_mpd_client()
        mpd_db = client.listallinfo()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        for dictionary in mpd_db:
            if "file" in dictionary.keys():
                dictionary["PATH"] = dictionary.pop("file")
                dictionary["LENGTH"] = dictionary.pop("time")
                dictionary["TRACKNUMBER"] = dictionary.pop("track")
                if type(dictionary["TRACKNUMBER"]) is list:
                    dictionary["TRACKNUMBER"] = dictionary["TRACKNUMBER"][0]
                tracknum_tmp = dictionary["TRACKNUMBER"]

                if '/' in tracknum_tmp:
                    dictionary["TRACKNUMBER"] = tracknum_tmp[:-tracknum_tmp.rfind("/") - 1]
                elif tracknum_tmp.isdigit():
                    pass
                else:
                    dictionary["TRACKNUMBER"] = "0"

                self.dict_list.append(dictionary)

    def delete_tracks_from_database(self, path_list):
        tracks_to_remove = get_tracks_with(self.dict_list, "PATH", path_list)
        for track in tracks_to_remove:
            for path in path_list: # in case get_tracks_with found substrings that we didn't want removed like matching pieces of directories 
                if path in track["PATH"]:
                    self.dict_list.remove(track)

        dump_database(self)

    def add_tracks_from_dir(self, folder_directory):
        mask = r'**/*.[mf][pl][3a]*'
        pathlist_gen = Path(folder_directory).glob(mask)
        tracklist = []
        pathlist = []
        for path in pathlist_gen:
            tmp_tagdict = create_track(path, db_dir[0])
            pathlist.append(tmp_tagdict["PATH"])
            tracklist.append(tmp_tagdict)

        if len(get_tracks_with(self.dict_list, "PATH", [tracklist[0]["PATH"]])) > 0:
            print("Tracks already exist in database.")
            return False
        else:
            for track in tracklist:
                self.dict_list.append(track)

            self.sort_tracks("NORMAL")

            with open(install_dir + "/playlists/Recently Added.m3u",'a+') as recentfile:
                for track in self.dict_list:
                    if track["PATH"] in pathlist:
                        recentfile.write(track["PATH"] + '\n')

            return True

    def update_tracks_from_dir(self, folder_directory):
        mask = r'**/*.[mf][pl][3a]*'
        pathlist_gen = Path(folder_directory).glob(mask)
        tracklist = []
        for path in pathlist_gen:
            tmp_tagdict = create_track(path, db_dir[0])
            tracklist.append(tmp_tagdict)

        full_sample_track_path = tracklist[0]["PATH"]
        index = full_sample_track_path.rfind('/')
        no_track_path = full_sample_track_path[:-(len(full_sample_track_path) - index)]
        tracks_to_remove = get_tracks_with(self.dict_list, "PATH", [no_track_path])
        for track in tracks_to_remove:
            self.dict_list.remove(track)

        for track in tracklist:
            print("Updating: ", track["PATH"])
            self.dict_list.append(track)

        self.sort_tracks("NORMAL")

    def sort_tracks(self, method):
        if method == "NORMAL":
            normal_sort(self.dict_list)
        else:
            raise ValueError("Sorting method '" + method + "' invalid")

    def get_track(self, path):
        """Get a single track dict matching a path. Might be useless.
        Args:
            path (str): Path of track.
        Returns:
            dict: Track dict."""
        for track in self.dict_list:
            if path in track["PATH"]:
                return track

    def get_total_track_time(self):
        tracktime = 0
        for track in self.dict_list:
            tracktime += int(track["LENGTH"])

        return tracktime


    def get_all_tracks_with(self, attrkey, attrvalue, exattrkey, exattrvalue):
        """Return list of tracks with specified attributes.
        Args:
            attrkey (str): The attribute key or type.
            attrvalue (list): The attribute(s) being matched for.
            exattrkey (str): Atribute key or type.
            exattrvalue (list): The attribute(s) to be excluded.

        Returns:
            list: List of track dictionaries."""
        
        if attrkey == "PLAYLISTS":
            return self.playlists.playlist_dict_list

        #This code is very ugly. Find way to make it better.

        #If no filter options are provided, just return the whole thing.
        if attrkey == None and exattrkey == None: 
            return self.dict_list
        else:
            new_list = [] #temp list to store tracks included (attrkey, attrvalue)

            if not attrkey == None: #check if an include filter was provided
                for track in self.dict_list:
                        if attrkey in track.keys(): #check if the key exists to avoid errors
                            #check all of the values in the attrvalue list against
                            #the track values. If any of them match, then append the track
                            if any(val in track[attrkey] for val in attrvalue):
                                new_list.append(track)
            else: #this means just the exclude filters were provided, so get the whole list
                new_list = self.dict_list

            new_new_list = [] #temp list to store tracks excluded (exattrkey, exattrvalue)
            if not exattrkey == None:
                for track in new_list:
                    if exattrkey in track.keys(): #check if exclude key exists to avoid errors
                        #check all of the values in the exattrvalue list against the track
                        #values. If any of them match, do NOT append the track.
                        if not any(val in track[exattrkey] for val in exattrvalue):
                            new_new_list.append(track)
                    else:
                        new_new_list.append(track) #append the track if the key doesn't exist
            else:
                return new_list #if there is no exclude filter provided, then the job was done

            return new_new_list

    def add_playlists(self, playlists):
        self.playlists = playlists

class Playlists:
    def __init__(self, playlists_dir, dir_strs, database):
        self.playlist_dict_list = []
        self.database = database
        self.populate_playlist_tracks(playlists_dir, dir_strs)

    def populate_playlist_tracks(self, playlist_dir, dir_strs):
        pathlist_gen = Path(playlist_dir).glob('*.m3u')
        for path in pathlist_gen:
            with open(path) as playlist:
                head, playlist_file_name = os.path.split(path)
                playlist_file_name = playlist_file_name[:-4]
                for track_path in playlist:
                    if not track_path == '\n':
                        track_path = track_path.rstrip("\n\r")
                        logging.debug(track_path)
                        tmp_tagdict = next(track for track in self.database.dict_list if track["PATH"] == track_path)
                        tmp_tagdict["PLAYLIST"] = playlist_file_name
                        self.playlist_dict_list.append(tmp_tagdict.copy())
