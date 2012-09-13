# -*- coding: utf-8 -*-
"""Module used to launch rating dialogues and send ratings to trakt"""

import xbmcaddon
import utilities
import windows

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.traktr" )

def rating_check(current_video, watched_time, total_time, playlist_length):
    """Check if a video should be rated and if so launches the correct rating window"""
    settings = xbmcaddon.Addon("script.traktr")

    rate_movies = settings.getSetting("rate_movie")
    rate_episodes = settings.getSetting("rate_episode")
    rate_each_playlist_item = settings.getSetting("rate_each_playlist_item")
    rate_min_view_time = settings.getSetting("rate_min_view_time")

    if (watched_time/total_time)*100>=float(rate_min_view_time):
        if (playlist_length <= 1) or (rate_each_playlist_item == 'true'):
            if current_video['type'] == 'movie' and rate_movies == 'true':
                rate_movie(current_video['id'])
            if current_video['type'] == 'episode' and rate_episodes == 'true':
                rate_episode(current_video['id'])


def rate_movie(movieid=None, imdbid=None, title=None, year=None):
    """Launches the movie rating dialogue"""
    if movieid != None:
        match = utilities.getMovieDetailsFromXbmc(movieid, ['imdbnumber', 'title', 'year'])
        if not match:
            #add error message here
            return

        imdbid = match['imdbnumber']
        title = match['title']
        year = match['year']

    if utilities.getTraktRatingType() == "advanced":
        gui = windows.RateMovieDialog("rate_advanced.xml", __settings__.getAddonInfo('path'))
    else:
        gui = windows.RateMovieDialog("rate.xml", __settings__.getAddonInfo('path'))

    gui.initDialog(imdbid, title, year, utilities.getMovieRatingFromTrakt(imdbid, title, year))
    gui.doModal()
    del gui


def rate_episode(episode_id):
    """Launches the episode rating dialogue"""
    match = utilities.getEpisodeDetailsFromXbmc(episode_id, ['showtitle', 'season', 'episode'])
    if not match:
        #add error message here
        return

    tvdbid = None #match['tvdbnumber']
    title = match['showtitle']
    year = None #match['year']
    season = match['season']
    episode = match['episode']

    if utilities.getTraktRatingType() == "advanced":
        gui = windows.RateEpisodeDialog("rate_advanced.xml", __settings__.getAddonInfo('path'))
    else:
        gui = windows.RateEpisodeDialog("rate.xml", __settings__.getAddonInfo('path'))

    gui.initDialog(tvdbid, title, year, season, episode, utilities.getEpisodeRatingFromTrakt(tvdbid, title, year, season, episode))
    gui.doModal()
    del gui
