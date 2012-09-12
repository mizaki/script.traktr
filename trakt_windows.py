# -*- coding: utf-8 -*-
"""Module containing windows created from trakt data"""

import xbmcaddon
import xbmcgui

from utilities import _
import utilities
import windows

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon("script.traktr")

_WINDOW_TYPE_TV = 1
_WINDOW_TYPE_MOVIES = 2


def _create_window(name, items, window_type):
    """Create the actual window"""
    if window_type == _WINDOW_TYPE_MOVIES:
        gui = windows.MoviesWindow("movies.xml", __settings__.getAddonInfo('path'))
    elif window_type == _WINDOW_TYPE_TV:
        gui = windows.TVShowsWindow("tvshows.xml", __settings__.getAddonInfo('path'))

    gui.initWindow(items, name)
    gui.doModal()
    del gui


def recommended_movies():
    """Create recommended movies window"""
    movies = utilities.getRecommendedMoviesFromTrakt()
    watchlist = utilities.traktMovieListByImdbID(utilities.getWatchlistMoviesFromTrakt())

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(_(200), _(120))
        return

    for movie in movies:
        if movie['imdb_id'] in watchlist:
            movie['watchlist'] = True
        else:
            movie['watchlist'] = False

    _create_window('recommended', movies, _WINDOW_TYPE_MOVIES)


def recommended_tv():
    """Create recommended shows window"""
    tvshows = utilities.getRecommendedTVShowsFromTrakt()

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(_(200), _(121))
        return

    for tvshow in tvshows:
        tvshow['watchlist'] = tvshow['in_watchlist']

    _create_window('recommended', tvshows, _WINDOW_TYPE_TV)


def trending_movies():
    """Create tending movies window"""
    movies = utilities.getTrendingMoviesFromTrakt()
    watchlist = utilities.traktMovieListByImdbID(utilities.getWatchlistMoviesFromTrakt())

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(_(200), _(160))
        return

    for movie in movies:
        if movie['imdb_id'] in watchlist:
            movie['watchlist'] = True
        else:
            movie['watchlist'] = False

    _create_window('trending', movies, _WINDOW_TYPE_MOVIES)


def trending_tv():
    """Create trending shows window"""
    tvshows = utilities.getTrendingTVShowsFromTrakt()
    watchlist = utilities.traktShowListByTvdbID(utilities.getWatchlistTVShowsFromTrakt())

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(_(200), _(161))
        return

    for tvshow in tvshows:
        if tvshow['imdb_id'] in watchlist:
            tvshow['watchlist'] = True
        else:
            tvshow['watchlist'] = False

    _create_window('trending', tvshows, _WINDOW_TYPE_TV)


def watchlist_movies():
    """Create movie watchlist window"""
    movies = utilities.getWatchlistMoviesFromTrakt()

    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py

    if len(movies) == 0:
        xbmcgui.Dialog().ok(_(200), _(134))
        return

    _create_window('watchlist', movies, _WINDOW_TYPE_MOVIES)


def watchlist_tv():
    """Create TV show watchlist window"""
    tvshows = utilities.getWatchlistTVShowsFromTrakt()

    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py

    if len(tvshows) == 0:
        xbmcgui.Dialog().ok(_(200), _(135))
        return

    _create_window('watchlist', tvshows, _WINDOW_TYPE_TV)
