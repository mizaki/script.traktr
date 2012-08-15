# -*- coding: utf-8 -*-
#

import xbmc

try:
    import simplejson as json
except ImportError:
    import json

from utilities import Debug
import utilities as u

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

# Move this to its own file
def instantSyncPlayCount(data):
    if data['params']['data']['item']['type'] == 'episode':
        info = u.getEpisodeDetailsFromXbmc(data['params']['data']['item']['id'], ['tvshowid', 'showtitle', 'season', 'episode'])
        rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShowDetails', 'params':{'tvshowid': info['tvshowid'], 'properties': ['imdbnumber']}, 'id': 1})
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        Debug("[Instant-sync] (TheTVDB ID: )"+str(result))

        if info == None:
            return
        Debug("[Instant-sync] (episode playcount): "+str(info))

        if data['params']['data']['playcount'] == 0:
            res = u.setEpisodesUnseenOnTrakt(result['result']['tvshowdetails']['imdbnumber'], info['showtitle'], None, [{'season':info['season'], 'episode':info['episode']}])
        elif data['params']['data']['playcount'] == 1:
            res = u.setEpisodesSeenOnTrakt(result['result']['tvshowdetails']['imdbnumber'], info['showtitle'], None, [{'season':info['season'], 'episode':info['episode']}])
        else:
            return
        Debug("[Instant-sync] (episode playcount): responce "+str(res))

    if data['params']['data']['item']['type'] == 'movie':
        info = u.getMovieDetailsFromXbmc(data['params']['data']['item']['id'], ['imdbnumber', 'title', 'year', 'playcount', 'lastplayed'])
        if info == None:
            return

        Debug("[Instant-sync] (movie playcount): "+str(info))
        if 'lastplayed' not in info:
            info['lastplayed'] = None

        if data['params']['data']['playcount'] == 0:
            res = u.setMoviesUnseenOnTrakt([{'imdb_id':info['imdbnumber'], 'title':info['title'], 'year':info['year'], 'plays':data['params']['data']['playcount'], 'last_played':info['lastplayed']}])
        elif data['params']['data']['playcount'] == 1:
            res = u.setMoviesSeenOnTrakt([{'imdb_id':info['imdbnumber'], 'title':info['title'], 'year':info['year'], 'plays':data['params']['data']['playcount'], 'last_played':info['lastplayed']}])
        else:
            return
        Debug("[Instant-sync] (movie playcount): responce "+str(res))
