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

# list reccomended movies
def showRecommendedMovies():
    movies = utilities.getRecommendedMoviesFromTrakt()
    watchlist = utilities.traktMovieListByImdbID(utilities.getWatchlistMoviesFromTrakt())

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(120).encode( "utf-8", "ignore" )) # Trakt Utilities, there are no movies recommended for you
        return

    for movie in movies:
        if movie['imdb_id'] in watchlist:
            movie['watchlist'] = True
        else:
            movie['watchlist'] = False

    # display recommended movies list
    import windows
    gui = windows.MoviesWindow("movies.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(movies, 'recommended')
    gui.doModal()
    del gui

# list reccomended tv shows
def showRecommendedTVShows():
    tvshows = utilities.getRecommendedTVShowsFromTrakt()

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(121).encode( "utf-8", "ignore" )) # Trakt Utilities, there are no tv shows recommended for you
        return

    for tvshow in tvshows:
        tvshow['watchlist'] = tvshow['in_watchlist']

    # display recommended tv shows
    import windows
    gui = windows.TVShowsWindow("tvshows.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(tvshows, 'recommended')
    gui.doModal()
    del gui

