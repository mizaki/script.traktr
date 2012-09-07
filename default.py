# -*- coding: utf-8 -*-
#

import xbmcgui
import xbmcaddon
from utilities import Debug, checkSettings
import sync_update as su
import trending
import watchlist
import recommend

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

#read settings
__settings__ = xbmcaddon.Addon( "script.traktr" )
__language__ = __settings__.getLocalizedString

# Usermenu:
def menu():
    # check if needed settings are set
    if checkSettings() == False:
        return

    options = [__language__(201).encode( "utf-8", "ignore" ), __language__(202).encode( "utf-8", "ignore" ), __language__(203).encode( "utf-8", "ignore" ), __language__(204).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(200).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        else:
            if select == 0: # Watchlist
                submenuWatchlist()
            elif select == 1: # Recommendations
                submenuRecommendations()
            elif select == 2: # Trending Movies / TV Shows
                submenuTrendingMoviesTVShows()
            elif select == 3: # Update / Sync / Clean
                submenuUpdateSyncClean()


def submenuUpdateSyncClean():
    options = [__language__(300).encode( "utf-8", "ignore" ), __language__(301).encode( "utf-8", "ignore" ), __language__(302).encode( "utf-8", "ignore" ), __language__(303).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(200).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        elif select == 0: # Sync Movies
            su.syncMovies()
        elif select == 1: # Sync TV Shows
            su.syncTV()
        elif select == 2: # Clean Movie Collection
            su.cleanMovies()
        elif select == 3: # Clean TV Show Collection
            su.cleanTV()

def submenuTrendingMoviesTVShows():
    options = [__language__(310).encode( "utf-8", "ignore" ), __language__(311).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(203).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Trending Movies
            trending.showTrendingMovies()
        elif select == 1: # Trending TV Shows
            trending.showTrendingTVShows()

def submenuWatchlist():
    options = [__language__(320).encode( "utf-8", "ignore" ), __language__(321).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(201).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Watchlist Movies
            watchlist.showWatchlistMovies()
        elif select == 1: # Watchlist TV Shows
            watchlist.showWatchlistTVShows()

def submenuRecommendations():
    options = [__language__(330).encode( "utf-8", "ignore" ), __language__(331).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(202).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Watchlist Movies
            recommend.showRecommendedMovies()
        elif select == 1: # Watchlist TV Shows
            recommend.showRecommendedTVShows()

menu()
