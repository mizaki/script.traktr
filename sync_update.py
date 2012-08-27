# -*- coding: utf-8 -*-
#

import xbmc
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

import datetime
year = datetime.datetime.now().year

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
        progress.create("Trakt Utilities", __language__(1300).encode( "utf-8", "ignore" )) # Checking XBMC Database for new seen Movies

    # Generate list of movies keyed with their imdb id
    trakt_movies = utilities.traktMovieListByImdbID(utilities.getMoviesFromTrakt())
    xbmc_movies = utilities.xbmcMovieListByImdbID(utilities.getMoviesFromXBMC())

    playcount_update = []
    collection_update = []

    for imdbid in trakt_movies:
        if imdbid not in xbmc_movies:
            continue
        elif trakt_movies[imdbid]['plays'] > xbmc_movies[imdbid]['playcount']:
            utilities.setXBMCMoviePlaycount(xbmc_movies[imdbid]['movieid'], trakt_movies[imdbid]['plays'])
        elif trakt_movies[imdbid]['plays'] < xbmc_movies[imdbid]['playcount']:
            playcount_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year'], 'plays': xbmc_movies[imdbid]['playcount'], 'last_played': xbmc_movies[imdbid]['lastplayed']})

    for imdbid in xbmc_movies:
        if imdbid not in trakt_movies and xbmc_movies[imdbid]['playcount'] > 0:
            collection_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year']})
            playcount_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year'], 'plays': xbmc_movies[imdbid]['playcount'], 'last_played': xbmc_movies[imdbid]['lastplayed']})
        elif imdbid not in trakt_movies and xbmc_movies[imdbid]['playcount'] == 0:
            collection_update.append({'imdb_id': imdbid, 'title': xbmc_movies[imdbid]['title'], 'year': xbmc_movies[imdbid]['year']})

    if len(collection_update) > 0:
        utilities.traktJsonRequest('POST', '/movie/library/%%API_KEY%%', {'movies': collection_update})

    if len(playcount_update) > 0:
        utilities.setMoviesSeenOnTrakt(playcount_update)

    if not daemon:
        progress.close()

# updates tvshow collection entries on trakt (no unlibrary)
def updateTVShowCollection(daemon=False):

    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", __language__(1133).encode( "utf-8", "ignore" )) # Checking Database for new Episodes

    # get the required informations
    trakt_tvshowlist = utilities.getTVShowCollectionFromTrakt()
    xbmc_tvshows = utilities.getTVShowsFromXBMC()

    if xbmc_tvshows == None or trakt_tvshowlist == None: # error
        return

    trakt_tvshows = {}

    for i in range(0, len(trakt_tvshowlist)):
        trakt_tvshows[trakt_tvshowlist[i]['tvdb_id']] = trakt_tvshowlist[i]

    seasonid = -1
    seasonid2 = 0
    tvshows_toadd = []
    tvshow = {}
    foundseason = False

    for i in range(0, xbmc_tvshows['limits']['total']):
        if xbmc.abortRequested:
            raise SystemExit()
        if not daemon:
            progress.update(100 / xbmc_tvshows['limits']['total'] * i)
            if progress.iscanceled():
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1134).encode( "utf-8", "ignore" )) # Progress Aborted
                return

        seasons = utilities.getSeasonsFromXBMC(xbmc_tvshows['tvshows'][i])
        try:
            tvshow['title'] = xbmc_tvshows['tvshows'][i]['title']
        except KeyError:
            # no title? try label
            try:
                tvshow['title'] = xbmc_tvshows['tvshows'][i]['label']
            except KeyError:
                # no titel, no label ... sorry no upload ...
                continue

        try:
            tvshow['year'] = xbmc_tvshows['tvshows'][i]['year']
            tvshow['tvdb_id'] = xbmc_tvshows['tvshows'][i]['imdbnumber']
        except KeyError:
            # no year, no tvdb id ... sorry no upload ...
            continue

        tvshow['episodes'] = []

        for j in range(0, seasons['limits']['total']):
            while True:
                seasonid += 1
                episodes = utilities.getEpisodesFromXBMC(xbmc_tvshows['tvshows'][i], seasonid)

                if episodes['limits']['total'] > 0:
                    break
                if seasonid > 250 and seasonid < 1900:
                    seasonid = 1900  # check seasons that are numbered by year
                if seasonid > year+2:
                    break # some seasons off the end?!
            if seasonid > year+2:
                continue
            try:
                foundseason = False
                for k in range(0, len(trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'])):
                    if trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'][k]['season'] == seasonid:
                        foundseason = True
                        for l in range(0, len(episodes['episodes'])):
                            if episodes['episodes'][l]['episode'] in trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'][k]['episodes']:
                                pass
                            else:
                                # add episode
                                tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][l]['episode']})
                if foundseason == False:
                    # add season
                    for k in range(0, len(episodes['episodes'])):
                        tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][k]['episode']})
            except KeyError:
                # add season (whole tv show missing)
                for k in range(0, len(episodes['episodes'])):
                    tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][k]['episode']})

        seasonid = -1
        # if there are episodes to add to trakt - append to list
        if len(tvshow['episodes']) > 0:
            tvshows_toadd.append(tvshow)
            tvshow = {}
        else:
            tvshow = {}

    if not daemon:
        progress.close()

    count = 0
    for i in range(0, len(tvshows_toadd)):
        for j in range(0, len(tvshows_toadd[i]['episodes'])):
            count += 1

    tvshows_string = ""
    for i in range(0, len(tvshows_toadd)):
        if i == 0:
            tvshows_string += tvshows_toadd[i]['title']
        elif i > 5:
            break
        else:
            tvshows_string += ", " + tvshows_toadd[i]['title']

    # add episodes to library (collection):
    if count > 0:
        if daemon:
            utilities.notification("Trakt Utilities", str(count) + " " + __language__(1131).encode( "utf-8", "ignore" )) # TVShow Episodes will be added to Trakt Collection
        else:
            choice = xbmcgui.Dialog().yesno("Trakt Utilities", str(count) + " " + __language__(1131).encode( "utf-8", "ignore" ), tvshows_string) # TVShow Episodes will be added to Trakt Collection
            if choice == False:
                return

        error = None

        # refresh connection (don't want to get tcp timeout)
        conn = utilities.getTraktConnection()

        for i in range(0, len(tvshows_toadd)):
            if xbmc.abortRequested:
                raise SystemExit()
            data = utilities.traktJsonRequest('POST', '/show/episode/library/%%API_KEY%%', {'tvdb_id': tvshows_toadd[i]['tvdb_id'], 'title': tvshows_toadd[i]['title'], 'year': tvshows_toadd[i]['year'], 'episodes': tvshows_toadd[i]['episodes']}, returnStatus=True, conn = conn)

            if data['status'] == 'success':
                Debug ("successfully uploaded collection: " + str(data['message']))
            elif data['status'] == 'failure':
                Debug ("Error uploading tvshow collection: " + str(data['error']))
                error = data['error']

        if error == None:
            if not daemon:
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1137).encode( "utf-8", "ignore" )) # Episodes sucessfully updated to Trakt
        else:
            if daemon:
                utilities.notification("Trakt Utilities", __language__(1135).encode( "utf-8", "ignore" ) + str(error)) # Error uploading TVShow collection
            else:
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1135).encode( "utf-8", "ignore" ), error) # Error uploading TVShow collection
    else:
        if not daemon:
            xbmcgui.Dialog().ok("Trakt Utilities", __language__(1136).encode( "utf-8", "ignore" )) # No new episodes in XBMC library to update

# removes deleted tvshow episodes from trakt collection (unlibrary)
def cleanTVShowCollection(daemon=False):

    # display warning
    if not daemon:
        choice = xbmcgui.Dialog().yesno("Trakt Utilities", __language__(1156).encode( "utf-8", "ignore" ), __language__(1154).encode( "utf-8", "ignore" ), __language__(1155).encode( "utf-8", "ignore" )) #
        if choice == False:
            return

    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", __language__(1140).encode( "utf-8", "ignore" )) # Checking Database for deleted Episodes

    # get the required informations
    trakt_tvshowlist = utilities.getTVShowCollectionFromTrakt()
    xbmc_tvshows = utilities.getTVShowsFromXBMC()

    if xbmc_tvshows == None or trakt_tvshowlist == None: # error
        return

    trakt_tvshows = {}

    for i in range(0, len(trakt_tvshowlist)):
        trakt_tvshows[trakt_tvshowlist[i]['tvdb_id']] = trakt_tvshowlist[i]

    to_unlibrary = []

    xbmc_tvshows_tvdbid = {}
    tvshow = {}
    seasonid = -1
    foundseason = False
    progresscount = -1

    # make xbmc tvshows searchable by tvdbid
    for i in range(0, xbmc_tvshows['limits']['total']):
        try:
            xbmc_tvshows_tvdbid[xbmc_tvshows['tvshows'][i]['imdbnumber']] = xbmc_tvshows['tvshows'][i]
        except KeyError:
            continue # missing data, skip tvshow

    for trakt_tvshow in trakt_tvshows.items():
        if xbmc.abortRequested:
            raise SystemExit()
        if not daemon:
            progresscount += 1
            progress.update(100 / len(trakt_tvshows) * progresscount)
            if progress.iscanceled():
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1134).encode( "utf-8", "ignore" )) # Progress Aborted
                return

        try:
            tvshow['title'] = trakt_tvshow[1]['title']
            tvshow['year'] = trakt_tvshow[1]['year']
            tvshow['tvdb_id'] = trakt_tvshow[1]['tvdb_id']
        except KeyError:
            # something went wrong
            Debug("cleanTVShowCollection: KeyError trakt_tvshow[1] title, year or tvdb_id")
            continue # skip this tvshow

        tvshow['episodes'] = []
        try:
            xbmc_tvshow = xbmc_tvshows_tvdbid[trakt_tvshow[1]['tvdb_id']]
            # check seasons
            xbmc_seasons = utilities.getSeasonsFromXBMC(xbmc_tvshow)
            for i in range(0, len(trakt_tvshow[1]['seasons'])):
                count = 0



                for j in range(0, xbmc_seasons['limits']['total']):
                    while True:
                        seasonid += 1
                        xbmc_episodes = utilities.getEpisodesFromXBMC(xbmc_tvshow, seasonid)
                        if xbmc_episodes['limits']['total'] > 0:
                            count += 1
                            if trakt_tvshow[1]['seasons'][i]['season'] == seasonid:
                                foundseason = True
                                # check episodes
                                for k in range(0, len(trakt_tvshow[1]['seasons'][i]['episodes'])):
                                    episodeid = trakt_tvshow[1]['seasons'][i]['episodes'][k]
                                    found = False
                                    for l in range(0, xbmc_episodes['limits']['total']):
                                        if xbmc_episodes['episodes'][l]['episode'] == episodeid:
                                            found = True
                                            break
                                    if found == False:
                                        # delte episode from trakt collection
                                        tvshow['episodes'].append({'season': seasonid, 'episode': episodeid})
                                break
                        if count >= xbmc_seasons['limits']['total']:
                            break
                        if seasonid > 250 and seasonid < 1900:
                            seasonid = 1900  # check seasons that are numbered by year
                        if seasonid > year+2:
                            break # some seasons off the end?!
                    if seasonid > year+2:
                        continue
                if foundseason == False:
                    Debug("Season not found: " + repr(trakt_tvshow[1]['title']) + ": " + str(trakt_tvshow[1]['seasons'][i]['season']))
                    # delte season from trakt collection
                    for episodeid in trakt_tvshow[1]['seasons'][i]['episodes']:
                        tvshow['episodes'].append({'season': trakt_tvshow[1]['seasons'][i]['season'], 'episode': episodeid})
                foundseason = False
                seasonid = -1

        except KeyError:
            Debug ("TVShow not found: " + repr(trakt_tvshow[1]['title']))
            # delete tvshow from trakt collection
            for season in trakt_tvshow[1]['seasons']:
                for episode in season['episodes']:
                    tvshow['episodes'].append({'season': season['season'], 'episode': episode})

        if len(tvshow['episodes']) > 0:
            to_unlibrary.append(tvshow)
        tvshow = {}

    if not daemon:
        progress.close()

    for i in range(0, len(to_unlibrary)):
        episodes_debug_string = ""
        for j in range(0, len(to_unlibrary[i]['episodes'])):
            episodes_debug_string += "S" + str(to_unlibrary[i]['episodes'][j]['season']) + "E" + str(to_unlibrary[i]['episodes'][j]['episode']) + " "
        Debug("Found for deletion: " + to_unlibrary[i]['title'] + ": " + episodes_debug_string)

    count = 0
    for tvshow in to_unlibrary:
        count += len(tvshow['episodes'])

    tvshows_string = ""
    for i in range(0, len(to_unlibrary)):
        if to_unlibrary[i]['title'] is None:
            to_unlibrary[i]['title'] = "Unknown"
        if i == 0:
            tvshows_string += to_unlibrary[i]['title']
        elif i > 5:
            break
        else:
            tvshows_string += ", " + to_unlibrary[i]['title']

    # add episodes to library (collection):
    if count > 0:
        if not daemon:
            choice = xbmcgui.Dialog().yesno("Trakt Utilities", str(count) + " " + __language__(1141).encode( "utf-8", "ignore" ), tvshows_string) # TVShow Episodes will be removed from Trakt Collection
            if choice == False:
                return

        error = None

        # refresh connection (don't want to get tcp timeout)
        conn = utilities.getTraktConnection()

        for i in range(0, len(to_unlibrary)):
            if xbmc.abortRequested:
                raise SystemExit()
            data = utilities.traktJsonRequest('POST', '/show/episode/unlibrary/%%API_KEY%%', {'tvdb_id': to_unlibrary[i]['tvdb_id'], 'title': to_unlibrary[i]['title'], 'year': to_unlibrary[i]['year'], 'episodes': to_unlibrary[i]['episodes']}, returnStatus = True, conn = conn)

            if data['status'] == 'success':
                Debug ("successfully updated collection: " + str(data['message']))
            elif data['status'] == 'failure':
                Debug ("Error uploading tvshow collection: " + str(data['error']))
                error = data['error']

        if error == None:
            if daemon:
                utilities.notification("Trakt Utilities", __language__(1137).encode( "utf-8", "ignore" )) # Episodes sucessfully updated to Trakt
            else:
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1137).encode( "utf-8", "ignore" )) # Episodes sucessfully updated to Trakt
        else:
            if daemon:
                utilities.notification("Trakt Utilities", __language__(1135).encode( "utf-8", "ignore" ) + unicode(error)) # Error uploading TVShow collection
            else:
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1135).encode( "utf-8", "ignore" ), error) # Error uploading TVShow collection
    else:
        if not daemon:
            xbmcgui.Dialog().ok("Trakt Utilities", __language__(1142).encode( "utf-8", "ignore" )) # No episodes to remove from trakt


# syncs seen tvshows between trakt and xbmc (no unlibrary)
def syncSeenTVShows(daemon=False):

    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", __language__(1143).encode( "utf-8", "ignore" )) # Checking XBMC Database for new seen Episodes

    # get the required informations
    trakt_tvshowlist = utilities.getWatchedTVShowsFromTrakt()
    xbmc_tvshows = utilities.getTVShowsFromXBMC()

    if xbmc_tvshows == None or trakt_tvshowlist == None: # error
        return

    trakt_tvshows = {}

    for i in range(0, len(trakt_tvshowlist)):
        trakt_tvshows[trakt_tvshowlist[i]['tvdb_id']] = trakt_tvshowlist[i]

    set_as_seen = []
    seasonid = -1
    tvshow = {}

    for i in range(0, xbmc_tvshows['limits']['total']):
        if xbmc.abortRequested:
            raise SystemExit()
        if not daemon:
            progress.update(100 / xbmc_tvshows['limits']['total'] * i)
            if progress.iscanceled():
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1134).encode( "utf-8", "ignore" )) # Progress Aborted
                break

        seasons = utilities.getSeasonsFromXBMC(xbmc_tvshows['tvshows'][i])
        try:
            tvshow['tvshowid'] = xbmc_tvshows['tvshows'][i]['tvshowid']
            tvshow['title'] = xbmc_tvshows['tvshows'][i]['title']
            tvshow['year'] = xbmc_tvshows['tvshows'][i]['year']
            tvshow['tvdb_id'] = xbmc_tvshows['tvshows'][i]['imdbnumber']
        except KeyError:
            continue # missing data, skip

        tvshow['episodes'] = []

        for j in range(0, seasons['limits']['total']):
            while True:
                seasonid += 1
                episodes = utilities.getEpisodesFromXBMC(xbmc_tvshows['tvshows'][i], seasonid)
                if episodes['limits']['total'] > 0:
                    break
                if seasonid > 250 and seasonid < 1900:
                    seasonid = 1900  # check seasons that are numbered by year
                if seasonid > year+2:
                    break # some seasons off the end?!
            if seasonid > year+2:
                continue
            try:
                foundseason = False
                for k in range(0, len(trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'])):
                    if trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'][k]['season'] == seasonid:
                        foundseason = True
                        for l in range(0, len(episodes['episodes'])):
                            if episodes['episodes'][l]['episode'] in trakt_tvshows[xbmc_tvshows['tvshows'][i]['imdbnumber']]['seasons'][k]['episodes']:
                                pass
                            else:
                                # add episode as seen if playcount > 0
                                try:
                                    if episodes['episodes'][l]['playcount'] > 0:
                                        tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][l]['episode']})
                                except KeyError:
                                    pass
                if foundseason == False:
                    # add season
                    for k in range(0, len(episodes['episodes'])):
                        try:
                            if episodes['episodes'][k]['playcount'] > 0:
                                tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][k]['episode']})
                        except KeyError:
                            pass
            except KeyError:
                # add season as seen (whole tv show missing)
                for k in range(0, len(episodes['episodes'])):
                    try:
                        if episodes['episodes'][k]['playcount'] > 0:
                            tvshow['episodes'].append({'season': seasonid, 'episode': episodes['episodes'][k]['episode'], 'episodeid': episodes['episodes'][k]['episodeid']})
                    except KeyError:
                        pass

        seasonid = -1
        # if there are episodes to add to trakt - append to list
        if len(tvshow['episodes']) > 0:
            set_as_seen.append(tvshow)
            tvshow = {}
        else:
            tvshow = {}

    if not daemon:
        progress.close()

    count = 0
    set_as_seen_titles = ""
    for i in range(0, len(set_as_seen)):
        if i == 0:
            set_as_seen_titles += set_as_seen[i]['title']
        elif i > 5:
            break
        else:
            set_as_seen_titles += ", " + set_as_seen[i]['title']
        for j in range(0, len(set_as_seen[i]['episodes'])):
            count += 1

    # add seen episodes to trakt library:
    if count > 0:
        if daemon:
            choice = True
        else:
            choice = xbmcgui.Dialog().yesno("Trakt Utilities", str(count) + " " + __language__(1144).encode( "utf-8", "ignore" ), set_as_seen_titles) # TVShow Episodes will be added as seen on Trakt

        if choice == True:

            error = None

            # refresh connection (don't want to get tcp timeout)
            conn = utilities.getTraktConnection()

            for i in range(0, len(set_as_seen)):
                if xbmc.abortRequested:
                    raise SystemExit()
                data = utilities.traktJsonRequest('POST', '/show/episode/seen/%%API_KEY%%', {'tvdb_id': set_as_seen[i]['tvdb_id'], 'title': set_as_seen[i]['title'], 'year': set_as_seen[i]['year'], 'episodes': set_as_seen[i]['episodes']}, returnStatus = True, conn = conn)
                if data['status'] == 'failure':
                    Debug("Error uploading tvshow: " + repr(set_as_seen[i]['title']) + ": " + str(data['error']))
                    error = data['error']
                else:
                    Debug("Successfully uploaded tvshow " + repr(set_as_seen[i]['title']) + ": " + str(data['message']))

            if error == None:
                if daemon:
                    utilities.notification("Trakt Utilities", __language__(1137).encode( "utf-8", "ignore" )) # Episodes sucessfully updated to Trakt
                else:
                    xbmcgui.Dialog().ok("Trakt Utilities", __language__(1137).encode( "utf-8", "ignore" )) # Episodes sucessfully updated to Trakt
            else:
                if daemon:
                    utilities.notification("Trakt Utilities", __language__(1145).encode( "utf-8", "ignore" ) + str(error)) # Error uploading seen TVShows
                else:
                    xbmcgui.Dialog().ok("Trakt Utilities", __language__(1145).encode( "utf-8", "ignore" ), error) # Error uploading seen TVShows
    else:
        if not daemon:
            xbmcgui.Dialog().ok("Trakt Utilities", __language__(1146).encode( "utf-8", "ignore" )) # No new seen episodes in XBMC library to update

    if not daemon:
        progress = xbmcgui.DialogProgress()
        progress.create("Trakt Utilities", __language__(1148).encode( "utf-8", "ignore" )) # Checking Trakt Database for new seen Episodes
    progress_count = 0

    xbmc_tvshows_tvdbid = {}

    # make xbmc tvshows searchable by tvdbid
    for i in range(0, xbmc_tvshows['limits']['total']):
        try:
            xbmc_tvshows_tvdbid[xbmc_tvshows['tvshows'][i]['imdbnumber']] = xbmc_tvshows['tvshows'][i]
        except KeyError:
            continue

    set_as_seen = []
    tvshow_to_set = {}

    # add seen episodes to xbmc
    for tvshow in trakt_tvshowlist:
        if xbmc.abortRequested:
            raise SystemExit()
        if not daemon:
            progress.update(100 / len(trakt_tvshowlist) * progress_count)
            progress_count += 1
            if progress.iscanceled():
                xbmcgui.Dialog().ok("Trakt Utilities", __language__(1134).encode( "utf-8", "ignore" )) # Progress Aborted
                return
        try:
            tvshow_to_set['title'] = tvshow['title']
            tvshow_to_set['tvdb_id'] = tvshow['tvdb_id']
        except KeyError:
            continue # missing data, skip to next tvshow

        tvshow_to_set['episodes'] = []

        Debug("checking: " + repr(tvshow['title']))

        trakt_seasons = tvshow['seasons']
        for trakt_season in trakt_seasons:
            seasonid = trakt_season['season']
            episodes = trakt_season['episodes']
            try:
                xbmc_tvshow = xbmc_tvshows_tvdbid[tvshow['tvdb_id']]
            except KeyError:
                Debug("tvshow not found in xbmc database")
                continue # tvshow not in xbmc library

            xbmc_episodes = utilities.getEpisodesFromXBMC(xbmc_tvshow, seasonid)
            if xbmc_episodes['limits']['total'] > 0:
                # sort xbmc episodes by id
                xbmc_episodes_byid = {}
                for i in xbmc_episodes['episodes']:
                    xbmc_episodes_byid[i['episode']] = i

                for episode in episodes:
                    xbmc_episode = None
                    try:
                        xbmc_episode = xbmc_episodes_byid[episode]
                    except KeyError:
                        pass
                    try:
                        if xbmc_episode != None:
                            if xbmc_episode['playcount'] <= 0:
                                tvshow_to_set['episodes'].append([seasonid, episode, xbmc_episode['episodeid']])
                    except KeyError:
                        # episode not in xbmc database
                        pass

        if len(tvshow_to_set['episodes']) > 0:
            set_as_seen.append(tvshow_to_set)
        tvshow_to_set = {}

    if not daemon:
        progress.close()

    count = 0
    set_as_seen_titles = ""
    Debug ("set as seen length: " + str(len(set_as_seen)))
    for i in range(0, len(set_as_seen)):
        if i == 0:
            set_as_seen_titles += set_as_seen[i]['title']
        elif i > 5:
            break
        else:
            set_as_seen_titles += ", " + set_as_seen[i]['title']
        for j in range(0, len(set_as_seen[i]['episodes'])):
            count += 1

    # add seen episodes to xbmc library:
    if count > 0:
        if daemon:
            choice = True
        else:
            choice = xbmcgui.Dialog().yesno("Trakt Utilities", str(count) + " " + __language__(1149).encode( "utf-8", "ignore" ), set_as_seen_titles) # TVShow Episodes will be set as seen on XBMC

        if choice == True:

            if not daemon:
                progress = xbmcgui.DialogProgress()
                progress.create("Trakt Utilities", __language__(1150).encode( "utf-8", "ignore" )) # updating XBMC Database
            progress_count = 0

            for tvshow in set_as_seen:
                if xbmc.abortRequested:
                    raise SystemExit()
                if not daemon:
                    progress.update(100 / len(set_as_seen) * progress_count)
                    progress_count += 1
                    if progress.iscanceled():
                        xbmcgui.Dialog().ok("Trakt Utilities", __language__(1134).encode( "utf-8", "ignore" )) # Progress Aborted
                        progress.close()
                        return

                for episode in tvshow['episodes']:
                    print episode
                    utilities.setXBMCEpisodePlaycount(episode[2], 1)

            if not daemon:
                progress.close()
    else:
        if not daemon:
            xbmcgui.Dialog().ok("Trakt Utilities", __language__(1151).encode( "utf-8", "ignore" )) # No new seen episodes on Trakt to update

