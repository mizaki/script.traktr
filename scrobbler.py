# -*- coding: utf-8 -*-
"""Contains the scrobbler class which scrobbles episodes and movies that are being watched"""

import xbmc
import xbmcaddon
import threading
import time
import sys

from utilities import Debug
import utilities
import rating

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

__settings__ = xbmcaddon.Addon("script.traktr")


class Scrobbler(threading.Thread):
    """Scrobbles movies and episodes that are being watched"""
    def __init__(self):
        super(Scrobbler, self).__init__()

        self._total_time = 1
        self._watched_time = 0
        self._start_time = 0
        self._current_video = None
        self._pinging = False
        self._playlist_length = 1
        self.abort_requested = False


    def run(self):
        # When requested ping trakt to say that the user is still watching the item
        count = 0
        while (not (self.abort_requested or xbmc.abortRequested)):
            time.sleep(5)
            if self._pinging:
                count += 1
                if count >= 100:
                    Debug("[Scrobbler] Pinging watching "+str(self._current_video))
                    tmp = time.time()
                    self._watched_time += tmp - self._start_time
                    self._start_time = tmp
                    self._started_watching()
                    count = 0
            else:
                count = 0

        Debug("Scrobbler stopping")


    def playback_started(self, data):
        self._current_video = data['item']
        if self._current_video != None:
            if 'type' in self._current_video and 'id' in self._current_video:
                Debug("[Scrobbler] Watching: "+self._current_video['type']+" - "+str(self._current_video['id']))
                try:
                    if not xbmc.Player().isPlayingVideo():
                        Debug("[Scrobbler] Suddenly stopped watching item")
                        return
                    time.sleep(1) # Wait for possible silent seek (caused by resuming)
                    self._watched_time = xbmc.Player().getTime()
                    self._total_time = xbmc.Player().getTotalTime()
                    if self._total_time == 0:
                        if self._current_video['type'] == 'movie':
                            self._total_time = 90
                        elif self._current_video['type'] == 'episode':
                            self._total_time = 30
                        else:
                            self._total_time = 1
                    self._playlist_length = utilities.getPlaylistLengthFromXBMCPlayer(data['player']['playerid'])
                    if (self._playlist_length == 0):
                        Debug("[Scrobbler] Warning: Cant find playlist length?!, assuming that this item is by itself")
                        self._playlist_length = 1
                except:
                    Debug("[Scrobbler] Suddenly stopped watching item, or error: " + str(sys.exc_info()[0]))
                    self._current_video = None
                    self._start_time = 0
                    return
                self._start_time = time.time()
                self._started_watching()
                self._pinging = True
            else:
                self._current_video = None
                self._start_time = 0


    def playback_paused(self):
        if self._start_time != 0:
            self._watched_time += time.time() - self._start_time
            Debug("[Scrobbler] Paused after: "+str(self._watched_time))
            self._start_time = 0


    def playback_ended(self):
        if self._start_time != 0:
            if self._current_video == None:
                Debug("[Scrobbler] Warning: Playback ended but video forgotten")
                return
            self._watched_time += time.time() - self._start_time
            self._pinging = False
            if self._watched_time != 0:
                if 'type' in self._current_video and 'id' in self._current_video:
                    self._check()
                    rating.rating_check(self._current_video, self._watched_time, self._total_time, self._playlist_length)
                self._watched_time = 0
            self._start_time = 0


    def _started_watching(self):
        scrobble_movies = __settings__.getSetting("scrobble_movie")
        scrobble_episodes = __settings__.getSetting("scrobble_episode")
       
        Debug('[Scrobbler] Started watching')
        if self._current_video['type'] == 'movie' and scrobble_movies == 'true':
            match = utilities.getMovieDetailsFromXbmc(self._current_video['id'], ['imdbnumber', 'title', 'year'])
            if match == None:
                return
            response = utilities.watchingMovieOnTrakt(match['imdbnumber'], match['title'], match['year'], self._total_time/60, int(100*self._watched_time/self._total_time))
            if response != None:
                Debug("[Scrobbler] Watch response: "+str(response))
        elif self._current_video['type'] == 'episode' and scrobble_episodes == 'true':
            match = utilities.getEpisodeDetailsFromXbmc(self._current_video['id'], ['showtitle', 'season', 'episode', 'uniqueid'])
            if match == None:
                return
            response = utilities.watchingEpisodeOnTrakt(None, match['showtitle'], None, match['season'], match['episode'], match['uniqueid']['unknown'], self._total_time/60, int(100*self._watched_time/self._total_time))
            if response != None:
                Debug("[Scrobbler] Watch responce: "+str(response))


    def _stopped_watching(self):
        scrobble_movies = __settings__.getSetting("scrobble_movie")
        scrobble_episodes = __settings__.getSetting("scrobble_episode")

        if self._current_video['type'] == 'movie' and scrobble_movies == 'true':
            response = utilities.cancelWatchingMovieOnTrakt()
            if response != None:
                Debug("[Scrobbler] Cancel watch responce: "+str(response))
        elif self._current_video['type'] == 'episode' and scrobble_episodes == 'true':
            responce = utilities.cancelWatchingEpisodeOnTrakt()
            if responce != None:
                Debug("[Scrobbler] Cancel watch responce: "+str(responce))


    def _scrobble(self):
        scrobble_movies = __settings__.getSetting("scrobble_movie")
        scrobble_episodes = __settings__.getSetting("scrobble_episode")

        if self._current_video['type'] == 'movie' and scrobble_movies == 'true':
            match = utilities.getMovieDetailsFromXbmc(self._current_video['id'], ['imdbnumber', 'title', 'year'])
            if match == None:
                return
            response = utilities.scrobbleMovieOnTrakt(match['imdbnumber'], match['title'], match['year'], self._total_time/60, int(100*self._watched_time/self._total_time))
            if response != None:
                Debug("[Scrobbler] Scrobble responce: "+str(response))
        elif self._current_video['type'] == 'episode' and scrobble_episodes == 'true':
            match = utilities.getEpisodeDetailsFromXbmc(self._current_video['id'], ['showtitle', 'season', 'episode', 'uniqueid'])
            if match == None:
                return
            response = utilities.scrobbleEpisodeOnTrakt(None, match['showtitle'], None, match['season'], match['episode'], match['uniqueid']['unknown'], self._total_time/60, int(100*self._watched_time/self._total_time))
            if response != None:
                Debug("[Scrobbler] Scrobble responce: "+str(response))


    def _check(self):
        reload_settings = xbmcaddon.Addon( "script.traktr" )
        min_view_time = reload_settings.getSetting("scrobble_min_view_time")

        if (self._watched_time/self._total_time)*100 >= float(min_view_time):
            self._scrobble()
        else:
            self._stopped_watching()
