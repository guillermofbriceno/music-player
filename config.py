import curses

#Database directory. Must match MPD music directories (multiple dirs not supported by MPD anyway)
db_dir = ["/home/guillermo/bach/Music/all-music"]
#db_dir = ["/home/guillermo/programming/music-player/test-music"]
playlists_dir = "/home/guillermo/programming/music-player/playlists"
install_dir = "/home/guillermo/programming/music-player"

#Keybindings
number_keys = [ord(str(num)) for num in range(9)]

mvmt_keys = {
            'j': 'move_down',
            'k': 'move_up',
            'h': 'move_left',
            'l': 'move_right',
            'n': 'play_track',
            't': 'jump_to_track_pane',
            's': 'toggle_random',
            'f': 'search_mode',
            '\x1b': 'reset_tab',
            ' ': 'select_track',
            'm': 'add_to_playlist_pane',
            '\n': 'add_to_playlist',
            '.': 'skip_down_pane',
            ',': 'skip_up_pane',
            'r': 'remove_tracks'
            }

#Interface configuration
ui_config = {
            'SCRLL-TH': 8,
            'refresh-delay': 15
            }

tabs_config = [
            {
                'tab-type': "SINGLE",
                'include-only': ["COMPOSER", ["Bach"]],
                'exclude': [None, None]
            },
            {
                'tab-type': "4-PANE",
                'include-only': ["COMPOSER", ["Bach"]],
                'exclude': [None, None],
                'filter-keys': ["GENRE", "ALBUM", "PERFORMER", "TRACK"],
                'pane-titles': ["Genre", "Work", "Performer", None]
            },
            {
                'tab-type': "3-PANE",
                'include-only': ["COMPOSER", ["Bach"]],
                'exclude': [None, None],
                'filter-keys': ["PERFORMER", "ALBUM", "TRACK"],
                'pane-titles': ["Performer", "Work", None]
            },
            {
                'tab-type': "3-PANE",
                'include-only': [None, None],
                'exclude': ["COMPOSER", ["Bach"]],
                'filter-keys': ["ARTIST", "ALBUM", "TRACK"],
                'pane-titles': ["Artist", "Album", None]
            },
            {
                'tab-type': "3-PANE",
                'include-only': [None, None],
                'exclude': ["COMPOSER", ["Bach"]],
                'filter-keys': ["GENRE", "ALBUM", "TRACK"],
                'pane-titles': ["Genre", "Album", None]
            },
            {
                'tab-type': "3-PANE",
                'include-only': ["PLAYLISTS", None],
                'exclude': [None, None],
                'filter-keys': ["PLAYLIST", "GENRE", "TRACK"],
                'pane-titles': ["Playlist", "Genre", None]
            }
        ]

#Example Tab Config
#tabs_config = [
#            {
#                'tab-type': "3-PANE",
#                'include-only': [None, None],
#                'exclude': ["COMPOSER", ["Bach"]],
#                'filter-keys': ["ARTIST", "ALBUM", "TRACK"],
#                'pane-titles': ["Artist", "Album", None]
#            },
#            {
#                'tab-type': "PLAYLIST"
#            },
#            {
#                'tab-type': "2-PANE",
#                'include-only': ["PLAYLISTS", None],
#                'exclude': [None, None],
#                'filter-keys': ["PLAYLIST", "TRACK"],
#                'pane-titles': ["Playlist", None]
#            }
#        ]


#Curses settings
def load_curses_config(stdscr):
    curses.curs_set(False)
    stdscr.nodelay(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, 124)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, 124)
    curses.init_pair(6, 124, curses.COLOR_BLACK) #list cursor color
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE) #selected tracks
    curses.init_pair(8, 232, 235)


############
#Don't touch
mvmt_keys = {ord(k): v for k, v in mvmt_keys.items()}
