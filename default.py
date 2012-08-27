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
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

#read settings
__settings__ = xbmcaddon.Addon( "script.traktutilities" )
__language__ = __settings__.getLocalizedString

Debug("default: " + __settings__.getAddonInfo("id") + " - version: " + __settings__.getAddonInfo("version"))

# Usermenu:
def menu():
    # check if needed settings are set
    if checkSettings() == False:
        return

    options = [__language__(1210).encode( "utf-8", "ignore" ), __language__(1212).encode( "utf-8", "ignore" ), __language__(1213).encode( "utf-8", "ignore" ), __language__(1214).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select("Trakt Utilities", options)
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
    options = [__language__(1218).encode( "utf-8", "ignore" ), __language__(1219).encode( "utf-8", "ignore" ), __language__(1220).encode( "utf-8", "ignore" ), __language__(1221).encode( "utf-8", "ignore" ), __language__(1222).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select("Trakt Utilities", options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        elif select == 0: # Sync Movies
            su.syncMovies()
        elif select == 1: # Update TV Show Collection
            su.updateTVShowCollection()
        elif select == 2: # Sync seen TV Shows
            su.syncSeenTVShows()
        elif select == 3: # Clean Movie Collection
            su.cleanMovies()
        elif select == 4: # Clean TV Show Collection
            su.cleanTVShowCollection()

def submenuTrendingMoviesTVShows():
    options = [__language__(1250).encode( "utf-8", "ignore" ), __language__(1251).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(1213).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Trending Movies
            trending.showTrendingMovies()
        elif select == 1: # Trending TV Shows
            trending.showTrendingTVShows()

def submenuWatchlist():
    options = [__language__(1252).encode( "utf-8", "ignore" ), __language__(1253).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(1210).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Watchlist Movies
            watchlist.showWatchlistMovies()
        elif select == 1: # Watchlist TV Shows
            watchlist.showWatchlistTVShows()

def submenuRecommendations():
    options = [__language__(1255).encode( "utf-8", "ignore" ), __language__(1256).encode( "utf-8", "ignore" )]

    while True:
        select = xbmcgui.Dialog().select(__language__(1212).encode( "utf-8", "ignore" ), options)
        Debug("Select: " + str(select))
        if select == -1:
            Debug ("menu quit by user")
            return
        if select == 0: # Watchlist Movies
            recommend.showRecommendedMovies()
        elif select == 1: # Watchlist TV Shows
            recommend.showRecommendedTVShows()

menu()
