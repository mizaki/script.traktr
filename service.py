# -*- coding: utf-8 -*-
#

import xbmc
import xbmcaddon

from utilities import Debug
import utilities
import notification_service as ns
import sync_update as su

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.traktutilities" )
__language__ = __settings__.getLocalizedString

Debug("service: " + __settings__.getAddonInfo("id") + " - version: " + __settings__.getAddonInfo("version"))

# starts update/sync
def autostart():
    if utilities.checkSettings(True):
        notificationThread = ns.NotificationService()
        notificationThread.start()

        autosync_movies = __settings__.getSetting("autosync_movies")
        autosync_tv = __settings__.getSetting("autosync_tv")
        autosync_cleanmoviecollection = __settings__.getSetting("autosync_cleanmovies")
        autosync_cleantvshowcollection = __settings__.getSetting("autosync_cleantv")
        try:
            if autosync_movies == "true":
                Debug("autostart sync seen movies")
                utilities.notification("Trakt Utilities", "Syncing Movies") # start sync movies

                su.syncMovies(daemon=True)

                if autosync_cleanmoviecollection == "true":
                    su.cleanMovies(daemon=True)

            if xbmc.abortRequested:
                raise SystemExit()

            if autosync_tv == "true":
                utilities.notification("Trakt Utilities", "Syncing TV") # start tvshow collection update

                su.syncTV(True)
                if autosync_cleantvshowcollection:
                    su.cleanTV(daemon=True)
            if xbmc.abortRequested:
                raise SystemExit()

            if autosync_tv == "true" or autosync_movies == "true":
                utilities.notification("Trakt Utilities", "Sync Complete") # update / sync done
        except SystemExit:
            notificationThread.abortRequested = True
            Debug("[Service] Auto sync processes aborted due to shutdown request")

        notificationThread.join()

autostart()
