# -*- coding: utf-8 -*-
#

import xbmc
import xbmcaddon
import xbmcgui
import time
import socket

try:
    import simplejson as json
except ImportError:
    import json

import nbconnection

import re

try:
    # Python 2.6 +
    from hashlib import sha as sha
except ImportError:
    # Python 2.5 and earlier
    import sha

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon( "script.traktr" )
__language__ = __settings__.getLocalizedString

apikey = '48dfcb4813134da82152984e8c4f329bc8b8b46a'
username = __settings__.getSetting("username")
pwd = sha.new(__settings__.getSetting("password")).hexdigest()
debug = __settings__.getSetting( "debug" )


def Debug(msg, force=False):
    if (debug == 'true' or force):
        try:
            print "Traktr: " + msg
        except UnicodeEncodeError:
            print "Traktr: " + msg.encode( "utf-8", "ignore" )

def _(string_id):
    """Returns the string from the language resource files specified by the id provided"""
    return __language__(string_id).encode("utf-8", "ignore")

import raw_xbmc_database

def getTraktRatingType():
    """Get the rating type set on trakt, either simple or advanced"""
    data = traktJsonRequest('POST', '/account/settings/%%API_KEY%%')
    return data['viewing']['ratings']['mode']


def getXBMCMajorVersion():
    """Get the major version number of the xbmc instance running

    10 = Dhama, 11 = Eden, 12 = Frodo
    """
    return int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])

def xcp(s):
    return re.sub('''(['])''', r"''", unicode(s))

def notification(header, message, time=5000, icon=__settings__.getAddonInfo("icon")):
    xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, time, icon ) )

def checkSettings(daemon=False):
    if username == "":
        if daemon:
            notification(__language__(200).encode( "utf-8", "ignore" ), __language__(100).encode( "utf-8", "ignore" )) # please enter your Username and Password in settings
        else:
            xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(100).encode( "utf-8", "ignore" )) # please enter your Username and Password in settings
            __settings__.openSettings()
        return False
    elif __settings__.getSetting("password") == "":
        if daemon:
            notification(__language__(200).encode( "utf-8", "ignore" ), __language__(101).encode( "utf-8", "ignore" )) # please enter your Password in settings
        else:
            xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(101).encode( "utf-8", "ignore" )) # please enter your Password in settings
            __settings__.openSettings()
        return False

    data = traktJsonRequest('POST', '/account/test/%%API_KEY%%', silent=True)
    if data == None: #Incorrect trakt login details
        if daemon:
            notification(__language__(200).encode( "utf-8", "ignore" ), __language__(104).encode( "utf-8", "ignore" )) # please enter your Password in settings
        else:
            xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(104).encode( "utf-8", "ignore" )) # please enter your Password in settings
            __settings__.openSettings()
        return False

    return True

# get a connection to trakt
def getTraktConnection():
    try:
        conn = nbconnection.NBConnection('api.trakt.tv')
    except socket.timeout:
        Debug("getTraktConnection: can't connect to trakt - timeout")
        return None
    return conn

# make a JSON api request to trakt
# method: http method (GET or POST)
# req: REST request (ie '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
# args: arguments to be passed by POST JSON (only applicable to POST requests), default:{}
# returnStatus: when unset or set to false the function returns None apon error and shows a notification,
#   when set to true the function returns the status and errors in ['error'] as given to it and doesn't show the notification,
#   use to customise error notifications
# anon: anonymous (dont send username/password), default:False
# connection: default it to make a new connection but if you want to keep the same one alive pass it here
# silent: default is False, when true it disable any error notifications (but not debug messages)
# passVersions: default is False, when true it passes extra version information to trakt to help debug problems
def traktJsonRequest(method, req, args={}, returnStatus=False, anon=False, conn=False, silent=False, passVersions=False):
    closeConnection = False
    if conn == False:
        conn = getTraktConnection()
        closeConnection = True
    if conn == None:
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Unable to connect to trakt'
            return data
        return None

    try:
        req = req.replace("%%API_KEY%%", apikey)
        req = req.replace("%%USERNAME%%", username)
        if method == 'POST':
            if not anon:
                args['username'] = username
                args['password'] = pwd
            if passVersions:
                args['plugin_version'] = __settings__.getAddonInfo("version")
                args['media_center'] = 'xbmc'
                args['media_center_version'] = xbmc.getInfoLabel("system.buildversion")
                args['media_center_date'] = xbmc.getInfoLabel("system.builddate")
            jdata = json.dumps(args)
            conn.request('POST', req, jdata)
        elif method == 'GET':
            conn.request('GET', req)
        else:
            return None
        Debug("trakt json url: "+req)
    except socket.error:
        Debug("traktQuery: can't connect to trakt")
        if not silent:
            Debug(__language__(102).encode( "utf-8", "ignore" )) # can't connect to trakt
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Socket error, unable to connect to trakt'
            return data
        return None

    conn.fire()

    while True:
        if xbmc.abortRequested:
            Debug("Broke loop due to abort")
            if returnStatus:
                data = {}
                data['status'] = 'failure'
                data['error'] = 'Abort requested, not waiting for responce'
                return data
            return None
        if conn.has_result():
            break
        time.sleep(0.1)

    response = conn.get_result()
    raw = response.read()
    if closeConnection:
        conn.close()

    try:
        data = json.loads(raw)
    except ValueError:
        Debug("traktQuery: Bad JSON responce: "+raw)
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Bad responce from trakt'
            return data
        if not silent:
            Debug("Traktr", __language__(103).encode( "utf-8", "ignore" ) + ": Bad responce from trakt") # Error
        return None

    if 'status' in data:
        if data['status'] == 'failure':
            Debug("traktQuery: Error: " + str(data['error']))
            if returnStatus:
                return data
            if not silent:
                Debug("Traktr", __language__(103).encode( "utf-8", "ignore" ) + ": " + str(data['error'])) # Error
            return None

    return data

# get movies from trakt server
def getMoviesFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getMoviesFromTrakt()'")
    return data

def xbmcMovieListByImdbID(data):
    xbmc_movies = {}

    for i in range(0, len(data)):
        xbmc_movies[data[i]['imdbnumber']] = data[i]

    return xbmc_movies

# get easy access to movie by imdb_id
def traktMovieListByImdbID(data):
    trakt_movies = {}

    for i in range(0, len(data)):
        if data[i]['imdb_id'] == "":
            continue
        trakt_movies[data[i]['imdb_id']] = data[i]

    return trakt_movies

# get easy access to tvshow by tvdb_id
def traktShowListByTvdbID(data):
    trakt_tvshows = {}

    for i in range(0, len(data)):
        trakt_tvshows[data[i]['tvdb_id']] = data[i]

    return trakt_tvshows

# set movies seen on trakt
#  - movies, required fields are 'plays', 'last_played' and 'title', 'year' or optionally 'imdb_id'
def setMoviesSeenOnTrakt(movies):
    data = traktJsonRequest('POST', '/movie/seen/%%API_KEY%%', {'movies': movies})
    if data == None:
        Debug("Error in request from 'setMoviesSeenOnTrakt()'")
    return data

# get tvshow collection from trakt server
def getTVShowCollectionFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/shows/collection.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getTVShowCollectionFromTrakt()'")
    return data

def getWatchedTVShowsFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/shows/watched.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchedTVShowsFromTrakt()'")
    return data

def getTVShowsFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params':{'properties': ['title', 'year', 'imdbnumber']}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getTVShowsFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['tvshows']
    except KeyError:
        Debug("getTVShowsFromXBMC: KeyError: result['result']")
        return None

# get episodes for a given tvshow / season from XBMC
def getEpisodesFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes', 'params':{'properties': ['tvshowid', 'episode', 'season', 'playcount']}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getEpisodesFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['episodes']
    except KeyError:
        Debug("getEpisodesFromXBMC: KeyError: result['result']")
        return None

# get a single episode from xbmc given the id
def getEpisodeDetailsFromXbmc(libraryId, fields):
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params':{'episodeid': libraryId, 'properties': fields}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getEpisodeDetailsFromXbmc: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['episodedetails']
    except KeyError:
        Debug("getEpisodeDetailsFromXbmc: KeyError: result['result']['episodedetails']")
        return None

# get movies from XBMC
def getMoviesFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovies', 'params':{'properties': ['title', 'year', 'originaltitle', 'imdbnumber', 'playcount', 'lastplayed']}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getMoviesFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['movies']
    except KeyError:
        Debug("getMoviesFromXBMC: KeyError: result['result']['movies']")
        return None

# get a single movie from xbmc given the id
def getMovieDetailsFromXbmc(libraryId, fields):
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovieDetails', 'params':{'movieid': libraryId, 'properties': fields}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getMovieDetailsFromXbmc: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['moviedetails']
    except KeyError:
        Debug("getMovieDetailsFromXbmc: KeyError: result['result']['moviedetails']")
        return None

# sets the playcount of a given movie by movieid
def setXBMCMoviePlaycount(movieid, playcount, imdb_id):
    if getXBMCMajorVersion() >= 12:
        time.sleep(0.2)
        xbmc.executeJSONRPC(json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.SetMovieDetails', 'params':{'movieid': movieid, 'playcount': playcount}, 'id': 1}))
        time.sleep(0.2)
    else:
        match = raw_xbmc_database.RawXbmcDb.query(
        "SELECT movie.idFile FROM movie"+
        " WHERE movie.c09='%(imdb_id)s'" % {'imdb_id':xcp(imdb_id)})

        if not match:
            #add error message here
            return

        try:
            match[0][0]
        except KeyError:
            return

        raw_xbmc_database.RawXbmcDb.execute(
        "UPDATE files"+
        " SET playcount=%(playcount)d" % {'playcount':int(playcount)}+
        " WHERE idFile=%(idFile)s" % {'idFile':xcp(match[0][0])})


# >= 12
def setXBMCBulkEpisodePlaycount(cmd):
    rpccmd = json.dumps(cmd)
    time.sleep(0.2)
    xbmc.executeJSONRPC(rpccmd)
    time.sleep(0.2)

# <12
# sets the playcount of a given episode by tvdb_id
def setXBMCEpisodePlaycount(tvdb_id, seasonid, episodeid, playcount):
    # httpapi till jsonrpc supports playcount update
    raw_xbmc_database.RawXbmcDb.execute(
    "UPDATE files"+
    " SET playcount=%(playcount)s" % {'playcount':xcp(playcount)}+
    " WHERE idFile IN ("+
    "  SELECT idFile"+
    "  FROM episode"+
    "  INNER JOIN tvshowlinkepisode ON episode.idEpisode = tvshowlinkepisode.idEpisode"+
    "   INNER JOIN tvshow ON tvshowlinkepisode.idShow = tvshow.idShow"+
    "   WHERE tvshow.c12='%(tvdb_id)s'" % {'tvdb_id':xcp(tvdb_id)}+
    "    AND episode.c12='%(seasonid)s'" % {'seasonid':xcp(seasonid)}+
    "    AND episode.c13='%(episodeid)s'" % {'episodeid':xcp(episodeid)}+
    " )")

# get the length of the current video playlist being played from XBMC
def getPlaylistLengthFromXBMCPlayer(playerid):
    if playerid == -1:
        return 1 #Default player (-1) can't be checked properly
    if playerid < 0 or playerid > 2:
        Debug("[Util] getPlaylistLengthFromXBMCPlayer, invalid playerid: "+str(playerid))
        return 0
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Player.GetProperties', 'params':{'playerid': playerid, 'properties':['playlistid']}, 'id': 1})
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    # check for error
    try:
        error = result['error']
        Debug("[Util] getPlaylistLengthFromXBMCPlayer, Player.GetProperties: " + str(error))
        return 0
    except KeyError:
        pass # no error
    playlistid = result['result']['playlistid']

    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Playlist.GetProperties', 'params':{'playlistid': playlistid, 'properties': ['size']}, 'id': 1})
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    # check for error
    try:
        error = result['error']
        Debug("[Util] getPlaylistLengthFromXBMCPlayer, Playlist.GetProperties: " + str(error))
        return 0
    except KeyError:
        pass # no error

    return result['result']['size']

def getMovieIdFromXBMC(imdb_id, title):
    rpccmd = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetMovies", "params": { "properties": ["imdbnumber"]}})
    result = json.loads(xbmc.executeJSONRPC(rpccmd))
    result = result["result"]["movies"]

    for movie in result:
        if movie["imdbnumber"] == imdb_id:
            return movie["movieid"]

    return -1


def getShowIdFromXBMC(tvdb_id, title):
    rpccmd = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetTVShows", "params": { "properties": ["imdbnumber"]}})
    result = json.loads(xbmc.executeJSONRPC(rpccmd))
    result = result["result"]["tvshows"]

    for tvshow in result:
        if tvshow["imdbnumber"] == tvdb_id:
            return tvshow["tvshowid"]

    return -1

# returns list of movies from watchlist
def getWatchlistMoviesFromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/movies.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

# returns list of tv shows from watchlist
def getWatchlistTVShowsFromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/shows.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchlistTVShowsFromTrakt()'")
    return data

# add an array of movies to the watch-list
def addMoviesToWatchlist(data):
    movies = []
    for item in data:
        movie = {}
        if "imdb_id" in item:
            movie["imdb_id"] = item["imdb_id"]
        if "tmdb_id" in item:
            movie["tmdb_id"] = item["tmdb_id"]
        if "title" in item:
            movie["title"] = item["title"]
        if "year" in item:
            movie["year"] = item["year"]
        movies.append(movie)

    data = traktJsonRequest('POST', '/movie/watchlist/%%API_KEY%%', {"movies":movies})
    if data == None:
        Debug("Error in request from 'addMoviesToWatchlist()'")
    return data

# remove an array of movies from the watch-list
def removeMoviesFromWatchlist(data):
    movies = []
    for item in data:
        movie = {}
        if "imdb_id" in item:
            movie["imdb_id"] = item["imdb_id"]
        if "tmdb_id" in item:
            movie["tmdb_id"] = item["tmdb_id"]
        if "title" in item:
            movie["title"] = item["title"]
        if "year" in item:
            movie["year"] = item["year"]
        movies.append(movie)

    data = traktJsonRequest('POST', '/movie/unwatchlist/%%API_KEY%%', {"movies":movies})
    if data == None:
        Debug("Error in request from 'removeMoviesFromWatchlist()'")
    return data

# add an array of tv shows to the watch-list
def addTVShowsToWatchlist(data):
    shows = []
    for item in data:
        show = {}
        if "tvdb_id" in item:
            show["tvdb_id"] = item["tvdb_id"]
        if "imdb_id" in item:
            show["tmdb_id"] = item["imdb_id"]
        if "title" in item:
            show["title"] = item["title"]
        if "year" in item:
            show["year"] = item["year"]
        shows.append(show)

    data = traktJsonRequest('POST', '/show/watchlist/%%API_KEY%%', {"shows":shows})
    if data == None:
        Debug("Error in request from 'addMoviesToWatchlist()'")
    return data

# remove an array of tv shows from the watch-list
def removeTVShowsFromWatchlist(data):
    shows = []
    for item in data:
        show = {}
        if "tvdb_id" in item:
            show["tvdb_id"] = item["tvdb_id"]
        if "imdb_id" in item:
            show["imdb_id"] = item["imdb_id"]
        if "title" in item:
            show["title"] = item["title"]
        if "year" in item:
            show["year"] = item["year"]
        shows.append(show)

    data = traktJsonRequest('POST', '/show/unwatchlist/%%API_KEY%%', {"shows":shows})
    if data == None:
        Debug("Error in request from 'removeMoviesFromWatchlist()'")
    return data

#Set the rating for a movie on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateMovieOnTrakt(imdbid, title, year, rating):
    if not (rating in ("love", "hate", "unrate", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")):
        #add error message
        return

    Debug("Rating movie:" + rating)

    data = traktJsonRequest('POST', '/rate/movie/%%API_KEY%%', {'imdb_id': imdbid, 'title': title, 'year': year, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateMovieOnTrakt()'")

    if (rating == "unrate"):
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(140).encode( "utf-8", "ignore" )) # Rating removed successfully
    else :
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(141).encode( "utf-8", "ignore" )) # Rating submitted successfully

    return data

#Get the rating for a movie from trakt
def getMovieRatingFromTrakt(imdbid, title, year):
    if imdbid == "" or imdbid == None:
        return None #would be nice to be smarter in this situation

    data = traktJsonRequest('POST', '/movie/summary.json/%%API_KEY%%/'+str(imdbid))
    if data == None:
        Debug("Error in request from 'getMovieRatingFromTrakt()'")
        return None

    if 'rating' in data:
        return data['rating']

    print data
    Debug("Error in request from 'getMovieRatingFromTrakt()'")
    return None

#Set the rating for a tv episode on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateEpisodeOnTrakt(tvdbid, title, year, season, episode, rating):
    if not (rating in ("love", "hate", "unrate", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")):
        #add error message
        return

    Debug("Rating episode:" + rating)

    data = traktJsonRequest('POST', '/rate/episode/%%API_KEY%%', {'tvdb_id': tvdbid, 'title': title, 'year': year, 'season': season, 'episode': episode, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateEpisodeOnTrakt()'")

    if (rating == "unrate"):
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(140).encode( "utf-8", "ignore" )) # Rating removed successfully
    else :
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(141).encode( "utf-8", "ignore" )) # Rating submitted successfully

    return data

#Get the rating for a tv episode from trakt
def getEpisodeRatingFromTrakt(tvdbid, title, year, season, episode):
    if tvdbid == "" or tvdbid == None:
        return None #would be nice to be smarter in this situation

    data = traktJsonRequest('POST', '/show/episode/summary.json/%%API_KEY%%/'+str(tvdbid)+"/"+season+"/"+episode)
    if data == None:
        Debug("Error in request from 'getEpisodeRatingFromTrakt()'")
        return None

    if 'rating' in data:
        return data['rating']

    print data
    Debug("Error in request from 'getEpisodeRatingFromTrakt()'")
    return None

#Set the rating for a tv show on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateShowOnTrakt(tvdbid, title, year, rating):
    if not (rating in ("love", "hate", "unrate", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")):
        #add error message
        return

    Debug("Rating show:" + rating)

    data = traktJsonRequest('POST', '/rate/show/%%API_KEY%%', {'tvdb_id': tvdbid, 'title': title, 'year': year, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateShowOnTrakt()'")

    if (rating == "unrate"):
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(140).encode( "utf-8", "ignore" )) # Rating removed successfully
    else :
        notification(__language__(200).encode( "utf-8", "ignore" ), __language__(141).encode( "utf-8", "ignore" )) # Rating submitted successfully

    return data

#Get the rating for a tv show from trakt
def getShowRatingFromTrakt(tvdbid, title, year):
    if tvdbid == "" or tvdbid == None:
        return None #would be nice to be smarter in this situation

    data = traktJsonRequest('POST', '/show/summary.json/%%API_KEY%%/'+str(tvdbid))
    if data == None:
        Debug("Error in request from 'getShowRatingFromTrakt()'")
        return None

    if 'rating' in data:
        return data['rating']

    print data
    Debug("Error in request from 'getShowRatingFromTrakt()'")
    return None

def getRecommendedMoviesFromTrakt():
    data = traktJsonRequest('POST', '/recommendations/movies/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getRecommendedMoviesFromTrakt()'")
    return data

def getRecommendedTVShowsFromTrakt():
    data = traktJsonRequest('POST', '/recommendations/shows/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getRecommendedTVShowsFromTrakt()'")
    return data

def getTrendingMoviesFromTrakt():
    data = traktJsonRequest('GET', '/movies/trending.json/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data

def getTrendingTVShowsFromTrakt():
    data = traktJsonRequest('GET', '/shows/trending.json/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getTrendingTVShowsFromTrakt()'")
    return data

def playMovieById(idMovie):
    # httpapi till jsonrpc supports selecting a single movie
    Debug("Play Movie requested for id: "+str(idMovie))
    if idMovie == -1:
        return # invalid movie id
    else:
        rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Player.Open', 'params': {'item': {'movieid': int(idMovie)}}, 'id': 1})
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        # check for error
        try:
            error = result['error']
            Debug("playMovieById, Player.Open: " + str(error))
            return None
        except KeyError:
            pass # no error

        try:
            if result['result'] == "OK":
                if xbmc.Player().isPlayingVideo():
                    return True
            notification(__language__(200).encode( "utf-8", "ignore" ), __language__(151).encode( "utf-8", "ignore" )) # Unable to play movie
        except KeyError:
            Debug("playMovieById, VideoPlaylist.Play: KeyError")
            return None

###############################
##### Scrobbling to trakt #####
###############################

#tell trakt that the user is watching a movie
def watchingMovieOnTrakt(imdb_id, title, year, duration, percent):
    responce = traktJsonRequest('POST', '/movie/watching/%%API_KEY%%', {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'watchingMovieOnTrakt()'")
    return responce

#tell trakt that the user is watching an episode
def watchingEpisodeOnTrakt(tvdb_id, title, year, season, episode, uniqueid, duration, percent):
    responce = traktJsonRequest('POST', '/show/watching/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'episode_tvdb_id': uniqueid, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'watchingEpisodeOnTrakt()'")
    return responce

#tell trakt that the user has stopped watching a movie
def cancelWatchingMovieOnTrakt():
    responce = traktJsonRequest('POST', '/movie/cancelwatching/%%API_KEY%%')
    if responce == None:
        Debug("Error in request from 'cancelWatchingMovieOnTrakt()'")
    return responce

#tell trakt that the user has stopped an episode
def cancelWatchingEpisodeOnTrakt():
    responce = traktJsonRequest('POST', '/show/cancelwatching/%%API_KEY%%')
    if responce == None:
        Debug("Error in request from 'cancelWatchingEpisodeOnTrakt()'")
    return responce

#tell trakt that the user has finished watching an movie
def scrobbleMovieOnTrakt(imdb_id, title, year, duration, percent):
    responce = traktJsonRequest('POST', '/movie/scrobble/%%API_KEY%%', {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'scrobbleMovieOnTrakt()'")
    return responce

#tell trakt that the user has finished watching an episode
def scrobbleEpisodeOnTrakt(tvdb_id, title, year, season, episode, uniqueid, duration, percent):
    responce = traktJsonRequest('POST', '/show/scrobble/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'episode_tvdb_id': uniqueid, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'scrobbleEpisodeOnTrakt()'")
    return responce

