# -*- coding: utf-8 -*-
#

import xbmcaddon
import xbmcgui

import utilities

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon( "script.traktutilities" )
__language__ = __settings__.getLocalizedString

# list watchlist movies
def showWatchlistMovies():
    movies = utilities.getWatchlistMoviesFromTrakt()

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(__language__(1201).encode( "utf-8", "ignore" ), __language__(1160).encode( "utf-8", "ignore" )) # Trakt Utilities, there are no movies in your watchlist
        return

    # display watchlist movie list
    import windows
    gui = windows.MoviesWindow("movies.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(movies, 'watchlist')
    gui.doModal()
    del gui

# list watchlist tv shows
def showWatchlistTVShows():
    tvshows = utilities.getWatchlistTVShowsFromTrakt()

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(__language__(1201).encode( "utf-8", "ignore" ), __language__(1161).encode( "utf-8", "ignore" )) # Trakt Utilities, there are no tv shows in your watchlist
        return

    # display watchlist tv shows
    import windows
    gui = windows.TVShowsWindow("tvshows.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(tvshows, 'watchlist')
    gui.doModal()
    del gui
