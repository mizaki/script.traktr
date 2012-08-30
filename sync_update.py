# -*- coding: utf-8 -*-
#

import xbmcaddon
import xbmcgui

from utilities import Debug
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


def _updateXBMCMoviePlaycounts(playcount_list, progress, daemon):
    """Updates playcounts from the list passed to it and updates the progress bar"""

    count = len(playcount_list)
    index = 0

    if not daemon:
        progress.update(0, "Setting XBMC Playcounts")

    for movieid, playcount in playcount_list:
        utilities.setXBMCMoviePlaycount(movieid, playcount)
        index += 1

        if not daemon:
            if progress.iscanceled():
                return
            progress.update(int(float(index)/count*100), "Setting XBMC Playcounts")


def cleanMovies(daemon=False):
    """Cleans trakt.tv movie database.

    Checks if trakt contains any movies that the xbmc database doesn't and if any
    are found unlibraries them on trakt.
    """
    trakt_movies = utilities.traktMovieListByImdbID(utilities.getMoviesFromTrakt())
    xbmc_movies = utilities.xbmcMovieListByImdbID(utilities.getMoviesFromXBMC())

    clean_list = []

    for imdbid in trakt_movies:
        if imdbid not in xbmc_movies:
            clean_list.append({'imdb_id': imdbid, 'title': trakt_movies[imdbid]['title'], 'year': trakt_movies[imdbid]['year']})

    if len(clean_list) > 0:
        utilities.traktJsonRequest('POST', '/movie/unlibrary/%%API_KEY%%', {'movies': clean_list})

def syncMovies(daemon=False):
    """Sync playcounts and collection status between trakt and xbmc.

    Scans XBMC and trakt and updates the play count of each movie in both the xbmc
    and trakt libraries based on which is higher. If the movie exists in xbmc
    but is not collected in trakt it is set as collected too.
    """
    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", "Generating Movie Lists") # Checking XBMC Database for new seen Movies

    # Generate list of movies keyed with their imdb id
    trakt_movies = utilities.traktMovieListByImdbID(utilities.getMoviesFromTrakt())
    xbmc_movies = utilities.xbmcMovieListByImdbID(utilities.getMoviesFromXBMC())

    xbmc_playcount_update = []
    trakt_playcount_update = []
    trakt_collection_update = []

    for imdbid in xbmc_movies:
        if imdbid not in trakt_movies:
            if xbmc_movies[imdbid]['playcount'] > 0:
                trakt_collection_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year']})
                trakt_playcount_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year'], 'plays': xbmc_movies[imdbid]['playcount'], 'last_played': xbmc_movies[imdbid]['lastplayed']})
            else:
                trakt_collection_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year']})
            continue

        if xbmc_movies[imdbid]['playcount'] > trakt_movies[imdbid]['plays']:
            trakt_playcount_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year'], 'plays': xbmc_movies[imdbid]['playcount'], 'last_played': xbmc_movies[imdbid]['lastplayed']})
        elif xbmc_movies[imdbid]['playcount'] < trakt_movies[imdbid]['plays']:
            xbmc_playcount_update.append((xbmc_movies[imdbid]['movieid'], trakt_movies[imdbid]['plays']))

    if not daemon:
        progress.update(0, "Updating Movies On Trakt")

    if len(trakt_collection_update) > 0:
        utilities.traktJsonRequest('POST', '/movie/library/%%API_KEY%%', {'movies': trakt_collection_update})

    if len(trakt_playcount_update) > 0:
        utilities.setMoviesSeenOnTrakt(trakt_playcount_update)

    if len(xbmc_playcount_update) > 0:
        _updateXBMCMoviePlaycounts(xbmc_playcount_update, progress, daemon)

    if not daemon:
        progress.close()


def _parseXBMCStructure():
    """Generate a useful structure for TV syncing from XBMC"""
    xbmc_raw_shows = utilities.getTVShowsFromXBMC()
    xbmc_raw_episodes = utilities.getEpisodesFromXBMC()
    xbmc_map_tvshowid_tvdbid = {}

    xbmc_shows = {}

    for show in xbmc_raw_shows:
        xbmc_map_tvshowid_tvdbid[show['tvshowid']] = show['imdbnumber']
        xbmc_shows[show['imdbnumber']] = {}
        xbmc_shows[show['imdbnumber']]['year'] = show['year']
        xbmc_shows[show['imdbnumber']]['title'] = show['title']
        xbmc_shows[show['imdbnumber']]['data'] = {}

    for episode in xbmc_raw_episodes:
        tvdbid = xbmc_map_tvshowid_tvdbid[episode['tvshowid']]
        season_num = episode['season']
        episode_num = episode['episode']

        if not season_num in xbmc_shows[tvdbid]['data']:
            xbmc_shows[tvdbid]['data'][season_num] = {}

        xbmc_shows[tvdbid]['data'][season_num][episode_num] = (episode['episodeid'], episode['playcount'])

    return xbmc_shows


def _parseTraktStructure():
    """Generate a useful structure for TV syncing with Trakt"""
    trakt_shows = {}
    trakt_collected = utilities.getTVShowCollectionFromTrakt()
    trakt_watched = utilities.getWatchedTVShowsFromTrakt()

    for show in trakt_collected:
        tvdbid = show['tvdb_id']
        trakt_shows[tvdbid] = {}
        trakt_shows[tvdbid]['title'] = show['title']
        trakt_shows[tvdbid]['year'] = show['year']
        trakt_shows[tvdbid]['data'] = {}

        for season in show['seasons']:
            seasonid = season['season']
            trakt_shows[tvdbid]['data'][seasonid] = {}

            for episode in season['episodes']:
                trakt_shows[tvdbid]['data'][seasonid][episode] = (True, False) # (Collected, Watched)

    for show in trakt_watched:
        tvdbid = show['tvdb_id']
        if tvdbid not in trakt_shows:
            trakt_shows[tvdbid] = {}
            trakt_shows[tvdbid]['title'] = show['title']
            trakt_shows[tvdbid]['year'] = show['year']
            trakt_shows[tvdbid]['data'] = {}

        for season in show['seasons']:
            seasonid = season['season']
            if seasonid not in trakt_shows[tvdbid]['data']:
                trakt_shows[tvdbid]['data'][seasonid] = {}

            for episode in season['episodes']:
                if episode not in trakt_shows[tvdbid]['data'][seasonid]:
                    trakt_shows[tvdbid]['data'][seasonid][episode] = (False, True)
                else:
                    trakt_shows[tvdbid]['data'][seasonid][episode] = (True, True)

    return trakt_shows


def _generateShowNotOnTrakt(shows, tvdbid):
    """Generate the collected and watched episodes from XBMC for a show that's not on trakt"""
    watched_episodes = {}
    collected_episodes = {}

    watched_episodes['tvdb_id'] = collected_episodes['tvdb_id'] = tvdbid
    watched_episodes['title'] = collected_episodes['title'] = shows[tvdbid]['title']
    watched_episodes['year'] = collected_episodes['year'] = shows[tvdbid]['year']
    watched_episodes['episodes'], collected_episodes['episodes'] = [], []

    for season_num in shows[tvdbid]['data']:
        for episode_num in shows[tvdbid]['data'][season_num]:
            playcount = shows[tvdbid]['data'][season_num][episode_num][1]
            if playcount > 0:
                watched_episodes['episodes'].append({'season': season_num, 'episode': episode_num})
            collected_episodes['episodes'].append({'season': season_num, 'episode': episode_num})

    if len(watched_episodes['episodes']) == 0:
        watched_episodes = None
    if len(collected_episodes['episodes']) == 0:
        collected_episodes = None

    return (collected_episodes, watched_episodes)

def _generateShowOnTrakt(xbmc_shows, trakt_shows, tvdbid):
    """Generate the collected and watched episodes from both XBMC and Trakt for a show that's on trakt"""
    watched_episodes = {}
    collected_episodes = {}

    watched_episodes['tvdb_id'] = collected_episodes['tvdb_id'] = tvdbid
    watched_episodes['title'] = collected_episodes['title'] = trakt_shows[tvdbid]['title']
    watched_episodes['year'] = collected_episodes['year'] = trakt_shows[tvdbid]['year']
    watched_episodes['episodes'], collected_episodes['episodes'] = [], []

    xbmc_new_plays = []

    for season_num in xbmc_shows[tvdbid]['data']:
        for episode_num in xbmc_shows[tvdbid]['data'][season_num]:
            xbmc_episodeid, xbmc_played = xbmc_shows[tvdbid]['data'][season_num][episode_num]
            try:
                trakt_collected, trakt_played = trakt_shows[tvdbid]['data'][season_num][episode_num]
            except KeyError:
                trakt_collected, trakt_played = False, False

            if not trakt_collected:
                collected_episodes['episodes'].append({'season': season_num, 'episode': episode_num})
            if not trakt_played and xbmc_played > 0:
                watched_episodes['episodes'].append({'season': season_num, 'episode': episode_num})
            if xbmc_played == 0 and trakt_played:
                xbmc_new_plays.append(xbmc_episodeid)

    if len(watched_episodes['episodes']) == 0:
        watched_episodes = None
    if len(collected_episodes['episodes']) == 0:
        collected_episodes = None

    return (collected_episodes, watched_episodes, xbmc_new_plays)


def _sendEpisodesToTrakt(collected, watched):
    """Send collected and watched statuses to trakt"""
    conn = utilities.getTraktConnection()
    for to_send in collected:
        utilities.traktJsonRequest('POST', '/show/episode/library/%%API_KEY%%', to_send, conn=conn)
    for to_send in watched:
        utilities.traktJsonRequest('POST', '/show/episodes/seen/%%API_KEY%%', to_send, conn=conn)

def syncTV(daemon=False):
    """Sync playcounts and collection status between trakt and xbmc.

    Scans XBMC and trakt and updates the playcount of each episode in both the
    xbmc and trakt libraries. If the episode exists in xbmc but is not collected
    on trakt it is also set as collected on trakt.
    """

    collect_episodes = []
    watch_episodes = []

    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", "Generating TV Episode Lists")

    xbmc_shows = _parseXBMCStructure()
    trakt_shows = _parseTraktStructure()

    index = 0
    length = len(xbmc_shows)

    for tvdbid in xbmc_shows:
        if not daemon:
            progress.update(int(float(index)/length*100), "Syncing Shows")

        index += 1

        if tvdbid not in trakt_shows:
            collect_trakt_episodes, watch_trakt_episodes = _generateShowNotOnTrakt(xbmc_shows, tvdbid)
        else:
            collect_trakt_episodes, watch_trakt_episodes, watched_xbmc_episodes = _generateShowOnTrakt(xbmc_shows, trakt_shows, tvdbid)

            xbmc_update = []
            for episodeid in watched_xbmc_episodes:
                xbmc_update.append({'jsonrpc': '2.0', 'method': 'VideoLibrary.SetEpisodeDetails', 'params':{'episodeid': episodeid, 'playcount': 1}, 'id': 1})
            if len(xbmc_update) > 0:
                utilities.setXBMCBulkEpisodePlaycount(xbmc_update)

        if collect_trakt_episodes:
            collect_episodes.append(collect_trakt_episodes)
        if watch_trakt_episodes:
            watch_episodes.append(watch_trakt_episodes)

    if not daemon:
        progress.update(0, "Sending Data To Trakt")

    _sendEpisodesToTrakt(collect_episodes, watch_episodes)

    if not daemon:
        progress.close()
