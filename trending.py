# -*- coding: utf-8 -*-
#

import xbmcaddon
import xbmcgui
import utilities

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon( "script.traktr" )
__language__ = __settings__.getLocalizedString


def showTrendingMovies():
    movies = utilities.getTrendingMoviesFromTrakt()
    watchlist = utilities.traktMovieListByImdbID(utilities.getWatchlistMoviesFromTrakt())

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(160).encode( "utf-8", "ignore" ))
        return

    for movie in movies:
        if movie['imdb_id'] in watchlist:
            movie['watchlist'] = True
        else:
            movie['watchlist'] = False

    # display trending movie list
    import windows
    gui = windows.MoviesWindow("movies.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(movies, 'trending')
    gui.doModal()
    del gui

def showTrendingTVShows():

    tvshows = utilities.getTrendingTVShowsFromTrakt()
    watchlist = utilities.traktShowListByTvdbID(utilities.getWatchlistTVShowsFromTrakt())

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(161).encode( "utf-8", "ignore" ))
        return

    for tvshow in tvshows:
        if tvshow['imdb_id'] in watchlist:
            tvshow['watchlist'] = True
        else:
            tvshow['watchlist'] = False

    # display trending tv shows
    import windows
    gui = windows.TVShowsWindow("tvshows.xml", __settings__.getAddonInfo('path'), "Default")
    gui.initWindow(tvshows, 'trending')
    gui.doModal()
    del gui
