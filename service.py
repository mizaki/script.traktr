# -*- coding: utf-8 -*-
"""Run at startup to sync items to trakt or clean the trakt library"""

import xbmc
import xbmcaddon

from utilities import Debug, _
import utilities
import notification_service as ns
import sync_update as su

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.traktr" )

Debug("service: " + __settings__.getAddonInfo("id") + " - version: " + __settings__.getAddonInfo("version"))

# starts update/sync
def autostart():
    """Run when xbmc stars up, runs tv or movie sync and cleans based on user settings"""
    if utilities.checkSettings(True):
        notification_thread = ns.NotificationService()
        notification_thread.start()

        autosync_movies = __settings__.getSetting("autosync_movies")
        autosync_tv = __settings__.getSetting("autosync_tv")
        autosync_cleanmoviecollection = __settings__.getSetting("autosync_cleanmovies")
        autosync_cleantvshowcollection = __settings__.getSetting("autosync_cleantv")

        try:
            if autosync_movies == "true":
                utilities.notification(_(200), _(110)) # start sync movies

                su.sync_movies(daemon=True)

                if autosync_cleanmoviecollection == "true":
                    su.clean_movies(daemon=True)

            if xbmc.abortRequested:
                raise SystemExit()

            if autosync_tv == "true":
                utilities.notification(_(200), _(111)) # start tvshow collection update

                su.sync_tv(daemon=True)

                if autosync_cleantvshowcollection:
                    su.clean_tv(daemon=True)

            if xbmc.abortRequested:
                raise SystemExit()

            if autosync_tv == "true" or autosync_movies == "true":
                utilities.notification(_(200), _(112)) # update / sync done
        except SystemExit:
            notification_thread.abort_requested = True
            Debug("[Service] Auto sync processes aborted due to shutdown request")

        notification_thread.join()

autostart()
