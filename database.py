import sys,os
from pathlib import Path
import taglib
import pickle
from fractions import Fraction
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
    """Return uniqified list of attributes matching attr.
    Args:
        dict_list (list of dicts): The list of dictionaries to be searched.
        attr (str): Attribute being matched for.

    Returns:
        list: List of string attribute values."""

    seen = set()
    seen_add = seen.add
    return [x[attr] for x in dict_list 
            if attr in x 
            if not (x[attr] in seen or seen_add(x[attr]))]

def start_database(directory_str):
    database_name = directory_str[directory_str.rfind("/") + 1:] + "-db"
    if database_file_already_exists(database_name):
        db_file = open(database_name, 'rb')
        database = pickle.load(db_file)
        return database
    else:
        print("Database file not found, creating one...")
        database = Database(directory_str)
        db_file = open(database_name, 'wb')
        pickle.dump(database, db_file)
        return database

def database_file_already_exists(file_name):
    return os.path.isfile(os.getcwd() + "/" + file_name)

class Database:
    def __init__(self, directory_str):
        self.dict_list = []
        self.directory_str = directory_str
        self.generate_database(directory_str)
        self.sort_tracks("NORMAL")

    def generate_database(self, directory_str):
        mask = r'**/*.[mf][pl][3a]*'
        pathlist = Path(directory_str).glob(mask)

        print("Generating database...\n")

        for path in pathlist:
            track = taglib.File(path)

            #Read the dict from taglib by removing the brackets from the values
            tmp_tagdict = {k: self.cut_brackets(tag) for k, tag in track.tags.items()}

            #Add length and path to the track dictionary. Absolute path cut MPC prep
            tmp_tagdict["PATH"] = str(path)[len(directory_str) + 1:]
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
        for track in self.dict_list:
            if path in track["PATH"]:
                return track
    
    def get_all_tracks_with(self, attrkey, attrvalue):
        """Return list of tracks with specified attributes.
        Args:
            attrkey (str): The attribute key or type.
            attrvalue (list): The attribute(s) being matched for.

        Returns:
            list: List of track dictionaries."""

        return [track for track in self.dict_list 
                if attrkey in track.keys() 
                if any(val in track[attrkey] for val in attrvalue)]

database_test = start_database("/home/guillermo/programming/music-player/test-music")

database_test.sort_tracks("NORMAL")
filteredtracks = database_test.dict_list
for track in filteredtracks:
    print(track["TRACKNUMBER"], track["TITLE"])
