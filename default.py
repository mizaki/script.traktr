# -*- coding: utf-8 -*-
"""Entry point when the Traktr menu is opened"""

import xbmcgui

from utilities import checkSettings, _
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


def _generate_menu(title, items):
    """Generate a menu with a title and a list of selections with a mapping of selections to function calls

    To create the mapping simply pass a tuple of tuples, the outer tuple holds them all together and the
    inner tuples specify a string to function call mapping, the string is used to name the item in the menu list
    and the function is called when the corresponding item is pressed"""
    selections, functions = zip(*items)

    while True:
        select = xbmcgui.Dialog().select(title, selections)
        if select == -1:
            return

        functions[select]()

def menu():
    """First menu shown when add-on menu is requested"""
    if checkSettings() == False:
        return

    options = (_(201), watchlist_menu), (_(202), recommendation_menu), (_(203), trending_menu), (_(204), sync_clean_menu)
    _generate_menu(_(200), options)


def sync_clean_menu():
    """Sync and clean submenu"""
    options = (_(300), su.syncMovies), (_(301), su.syncTV), (_(302), su.cleanMovies), (_(303), su.cleanTV)
    _generate_menu(_(204), options)


def trending_menu():
    """Trending items submenu, user selects either tv or movies to view the trending items of that type"""
    options = (_(310), trending.showTrendingMovies), (_(311), trending.showTrendingTVShows)
    _generate_menu(_(203), options)


def watchlist_menu():
    """Watchlist submenu, user selects either tv or movies to view the items of that type in the watchlist"""
    options = (_(320), watchlist.showWatchlistMovies), (_(321), watchlist.showWatchlistTVShows)
    _generate_menu(_(201), options)


def recommendation_menu():
    """Recommendations submenu, user selects either tv or movies to view the recommendations for each type"""
    options = (_(330), recommend.showRecommendedMovies), (_(331), recommend.showRecommendedTVShows)
    _generate_menu(_(202), options)


menu()
