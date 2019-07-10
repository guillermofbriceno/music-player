# music-player

Modular terminal music player for MPD.

---

This player acts as a front end to MPD using [python-mpd2](https://pypi.org/project/python-mpd2/), though there are still some MPC-based dependencies needed to be removed. It is focused on presenting your music library in an organized, modular fashion. 

Up to 9 'tabs' can be configured, each with a different combination and collection of filtered 'panes.' Each pane, usually from left to right, filters through the track library according to a set of given track tags. Each tab is configured in the `tabs_config` dictionary of the `config.py` file. All tags, including non-conventional ones, are supported.

Examples of different layouts and tag organizations:

![Alt text](https://www.emptytincan.com/i/g/1554147751-MOTgh.png "Genre->Album->Performer->Track")
Genre -> Album -> Performer -> Track. Custom pane titles can be set, here the 'Album' pane is set to 'Work.'

![Alt text](https://emptytincan.com/r/ba734 "Single pane with tracks")
Just a single pane with tracks. Each tab can be configured with include and exclude tags, in this example only tracks with the "Composer" tag matching "Bach" are allowed to be displayed in the tab.

![Alt text](https://emptytincan.com/r/g8ebn "Genre->Album->Track")
A more conventional three-pane layout, this time specifying an exclude with "Composer" "Bach." Excludes and includes can be mixed, and each can support more than one field and tag value.

# Todo

- Full python-mpd2 implementation
- Finish playlists
- Better handling of resizing and other bugs
