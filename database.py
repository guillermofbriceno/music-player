import sys,os
from pathlib import Path
import taglib
import pickle
from fractions import Fraction
from functools import reduce
import re

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s
    
def alphanum_key(track):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)',  track["ALBUM"] + track["TRACKNUMBER"])]

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
    return [x[attr] for x in dict_list 
            if attr in x 
            if not (x[attr] in seen or seen_add(x[attr]))]

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


def start_database(directory_strs):
    database_name = directory_strs[0][directory_strs[0].rfind("/") + 1:] + "-db"
    if database_file_already_exists(database_name):
        db_file = open(database_name, 'rb')
        database = pickle.load(db_file)
        return database
    else:
        print("Database file not found, creating one...")
        database = Database(directory_strs)
        db_file = open(database_name, 'wb')
        pickle.dump(database, db_file)
        return database

def database_file_already_exists(file_name):
    """Check if database file exists in the running/database directory.
    Args:
        file_name (str): The name of the file in the running directory.
    Returns:
        bool: Whether or not the file was found"""
    return os.path.isfile(os.getcwd() + "/" + file_name)

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
        mask = r'**/*.[mf][pl][3a]*'
        
        print("Generating database...\n")

        for dir_str in directory_strs:
            pathlist_gen = Path(dir_str).glob(mask)
            for path in pathlist_gen:

                track = taglib.File(path)

                #Read the dict from taglib by removing the brackets from the values
                tmp_tagdict = {k: self.cut_brackets(tag) for k, tag in track.tags.items()}

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

                self.dict_list.append(tmp_tagdict)

    def cut_brackets(self, tag):
        string = str(tag)
        string = string[2:]
        string = string[:-2]
        return string

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

    def get_all_tracks_with(self, attrkey, attrvalue, exattrkey, exattrvalue):
        """Return list of tracks with specified attributes.
        Args:
            attrkey (str): The attribute key or type.
            attrvalue (list): The attribute(s) being matched for.
            exattrkey (str): Atribute key or type.
            exattrvalue (list): The attribute(s) to be excluded.

        Returns:
            list: List of track dictionaries."""

        #This code is very ugly. Find way to make it better.b

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
