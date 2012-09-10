# -*- coding: utf-8 -*-
#

import xbmcaddon
import xbmcgui
from utilities import Debug
import utilities
import rating

import functools

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Andrew Etches"
__email__ = "andrew.etches@dur.ac.uk"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon( "script.traktr" )
__language__ = __settings__.getLocalizedString

BACKGROUND = 102
TITLE = 103
OVERVIEW = 104
POSTER = 105
PLAY_BUTTON = 106
YEAR = 107
RUNTIME = 108
TAGLINE = 109
MOVIE_LIST = 110
TVSHOW_LIST = 110
RATING = 111
WATCHERS = 112

RATE_SCENE = 98
RATE_TITLE = 100
RATE_CUR_NO_RATING = 101
RATE_CUR_LOVE = 102
RATE_CUR_HATE = 103
RATE_SKIP_RATING = 104
RATE_LOVE_BTN = 105
RATE_HATE_BTN = 106
RATE_RATE_SHOW_BG = 107
RATE_RATE_SHOW_BTN = 108
RATE_ADVANCED_1_BTN = 201
RATE_CUR_ADVANCED_1 = 211
RATE_ADVANCED_2_BTN = 202
RATE_CUR_ADVANCED_2 = 212
RATE_ADVANCED_3_BTN = 203
RATE_CUR_ADVANCED_3 = 213
RATE_ADVANCED_4_BTN = 204
RATE_CUR_ADVANCED_4 = 214
RATE_ADVANCED_5_BTN = 205
RATE_CUR_ADVANCED_5 = 215
RATE_ADVANCED_6_BTN = 206
RATE_CUR_ADVANCED_6 = 216
RATE_ADVANCED_7_BTN = 207
RATE_CUR_ADVANCED_7 = 217
RATE_ADVANCED_8_BTN = 208
RATE_CUR_ADVANCED_8 = 218
RATE_ADVANCED_9_BTN = 209
RATE_CUR_ADVANCED_9 = 219
RATE_ADVANCED_10_BTN = 210
RATE_CUR_ADVANCED_10 = 220


#get actioncodes from keymap.xml
ACTION_PARENT_DIRECTORY = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_CONTEXT_MENU = 117

class MoviesWindow(xbmcgui.WindowXML):
    movies = None
    type = 'basic'

    def initWindow(self, movies, type):
        self.movies = movies
        self.type = type

    def onInit(self):
        self.getControl(MOVIE_LIST).reset()
        if self.movies != None:
            for movie in self.movies:
                li = xbmcgui.ListItem(movie['title'], '', movie['images']['poster'])
                if not ('idMovie' in movie):
                    movie['idMovie'] = utilities.getMovieIdFromXBMC(movie['imdb_id'], movie['title'])
                if movie['idMovie'] != -1:
                    li.setProperty('Available','true')
                if self.type != 'watchlist':
                    if 'watchlist' in movie:
                        if movie['watchlist']:
                            li.setProperty('Watchlist','true')
                self.getControl(MOVIE_LIST).addItem(li)
            self.setFocus(self.getControl(MOVIE_LIST))
            self.listUpdate()
        else:
            Debug("MoviesWindow: Error: movies array is empty")
            self.close()

    def listUpdate(self):
        try:
            current = self.getControl(MOVIE_LIST).getSelectedPosition()
        except TypeError:
            return # ToDo: error output

        try:
            self.getControl(BACKGROUND).setImage(self.movies[current]['images']['fanart'])
        except KeyError:
            Debug("KeyError for Backround")
        except TypeError:
            Debug("TypeError for Backround")
        try:
            self.getControl(TITLE).setLabel(self.movies[current]['title'])
        except KeyError:
            Debug("KeyError for Title")
            self.getControl(TITLE).setLabel("")
        except TypeError:
            Debug("TypeError for Title")
        try:
            self.getControl(OVERVIEW).setText(self.movies[current]['overview'])
        except KeyError:
            Debug("KeyError for Overview")
            self.getControl(OVERVIEW).setText("")
        except TypeError:
            Debug("TypeError for Overview")
        try:
            self.getControl(YEAR).setLabel("Year: " + str(self.movies[current]['year']))
        except KeyError:
            Debug("KeyError for Year")
            self.getControl(YEAR).setLabel("")
        except TypeError:
            Debug("TypeError for Year")
        try:
            self.getControl(RUNTIME).setLabel("Runtime: " + str(self.movies[current]['runtime']) + " Minutes")
        except KeyError:
            Debug("KeyError for Runtime")
            self.getControl(RUNTIME).setLabel("")
        except TypeError:
            Debug("TypeError for Runtime")
        try:
            if self.movies[current]['tagline'] != "":
                self.getControl(TAGLINE).setLabel("\""+self.movies[current]['tagline']+"\"")
            else:
                self.getControl(TAGLINE).setLabel("")
        except KeyError:
            Debug("KeyError for Tagline")
            self.getControl(TAGLINE).setLabel("")
        except TypeError:
            Debug("TypeError for Tagline")
        try:
            self.getControl(RATING).setLabel("Rating: " + self.movies[current]['certification'])
        except KeyError:
            Debug("KeyError for Rating")
            self.getControl(RATING).setLabel("")
        except TypeError:
            Debug("TypeError for Rating")
        if 'watchers' in self.movies[current]:
            try:
                self.getControl(WATCHERS).setLabel(str(self.movies[current]['watchers']) + " people watching")
            except KeyError:
                Debug("KeyError for Watchers")
                self.getControl(WATCHERS).setLabel("")
            except TypeError:
                Debug("TypeError for Watchers")

    def onFocus( self, controlId ):
        self.controlId = controlId

    def showContextMenu(self):
        movie = self.movies[self.getControl(MOVIE_LIST).getSelectedPosition()]
        li = self.getControl(MOVIE_LIST).getSelectedItem()
        options = []
        actions = []
        if movie['idMovie'] != -1:
            options.append("Play")
            actions.append('play')
        if self.type != 'watchlist':
            if 'watchlist' in movie:
                if movie['watchlist']:
                    options.append(__language__(137).encode( "utf-8", "ignore" ))
                    actions.append('unwatchlist')
                else:
                    options.append(__language__(136).encode( "utf-8", "ignore" ))
                    actions.append('watchlist')
        else:
            options.append(__language__(137).encode( "utf-8", "ignore" ))
            actions.append('unwatchlist')
        options.append(__language__(138).encode( "utf-8", "ignore" ))
        actions.append('rate')

        select = xbmcgui.Dialog().select(movie['title']+" - "+str(movie['year']), options)
        if select != -1:
            Debug("Select: " + actions[select])
        if select == -1:
            Debug ("menu quit by user")
            return
        elif actions[select] == 'play':
            utilities.playMovieById(movie['idMovie'])
        elif actions[select] == 'unwatchlist':
            if utilities.removeMoviesFromWatchlist([movie]) == None:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(132).encode( "utf-8", "ignore" )) # Failed to remove from watch-list
            else:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(133).encode( "utf-8", "ignore" )) # Successfully removed from watch-list
                li.setProperty('Watchlist','false')
                movie['watchlist'] = False
        elif actions[select] == 'watchlist':
            if utilities.addMoviesToWatchlist([movie]) == None:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(130).encode( "utf-8", "ignore" )) # Failed to added to watch-list
            else:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(131).encode( "utf-8", "ignore" )) # Successfully added to watch-list
                li.setProperty('Watchlist','true')
                movie['watchlist'] = True
        elif actions[select] == 'rate':
            rating.doRateMovie(imdbid=movie['imdb_id'], title=movie['title'], year=movie['year'])

    def onAction(self, action):
        if action.getId() == 0:
            return
        if action.getId() in (ACTION_PARENT_DIRECTORY, ACTION_PREVIOUS_MENU):
            Debug("Closing MoviesWindow")
            self.close()
        elif action.getId() in (1, 2, 107):
            self.listUpdate()
        elif action.getId() == ACTION_SELECT_ITEM:
            movie = self.movies[self.getControl(MOVIE_LIST).getSelectedPosition()]
            if movie['idMovie'] == -1: # Error
                xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), movie['title'].encode( "utf-8", "ignore" ) + " " + __language__(150).encode( "utf-8", "ignore" )) # "moviename" not found in your XBMC Library
            else:
                utilities.playMovieById(movie['idMovie'])
        elif action.getId() == ACTION_CONTEXT_MENU:
            self.showContextMenu()
        else:
            Debug("Uncaught action (movies): "+str(action.getId()))

class MovieWindow(xbmcgui.WindowXML):

    movie = None

    def initWindow(self, movie):
        self.movie = movie

    def onInit(self):
        if self.movie != None:
            try:
                self.getControl(BACKGROUND).setImage(self.movie['images']['fanart'])
            except KeyError:
                Debug("KeyError for Backround")
            except TypeError:
                Debug("TypeError for Backround")
            try:
                self.getControl(POSTER).setImage(self.movie['images']['poster'])
            except KeyError:
                Debug("KeyError for Poster")
            except TypeError:
                Debug("TypeError for Poster")
            try:
                self.getControl(TITLE).setLabel(self.movie['title'])
            except KeyError:
                Debug("KeyError for Title")
            except TypeError:
                Debug("TypeError for Title")
            try:
                self.getControl(OVERVIEW).setText(self.movie['overview'])
            except KeyError:
                Debug("KeyError for Overview")
            except TypeError:
                Debug("TypeError for Overview")
            try:
                self.getControl(YEAR).setLabel("Year: " + str(self.movie['year']))
            except KeyError:
                Debug("KeyError for Year")
            except TypeError:
                Debug("TypeError for Year")
            try:
                self.getControl(RUNTIME).setLabel("Runtime: " + str(self.movie['runtime']) + " Minutes")
            except KeyError:
                Debug("KeyError for Runtime")
            except TypeError:
                Debug("TypeError for Runtime")
            try:
                self.getControl(TAGLINE).setLabel(self.movie['tagline'])
            except KeyError:
                Debug("KeyError for Runtime")
            except TypeError:
                Debug("TypeError for Runtime")
            try:
                self.playbutton = self.getControl(PLAY_BUTTON)
                self.setFocus(self.playbutton)
            except (KeyError, TypeError):
                pass

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onClick(self, controlId):
        if controlId == PLAY_BUTTON:
            pass

    def onAction(self, action):
        if action.getId() == 0:
            return
        if action.getId() in (ACTION_PARENT_DIRECTORY, ACTION_PREVIOUS_MENU):
            Debug("Closing MovieInfoWindow")
            self.close()
        else:
            Debug("Uncaught action (movie info): "+str(action.getId()))

class TVShowsWindow(xbmcgui.WindowXML):

    tvshows = None
    type = 'basic'

    def initWindow(self, tvshows, type):
        self.tvshows = tvshows
        self.type = type

    def onInit(self):
        if self.tvshows != None:
            for tvshow in self.tvshows:
                li = xbmcgui.ListItem(tvshow['title'], '', tvshow['images']['poster'])
                if not ('idShow' in tvshow):
                    tvshow['idShow'] = utilities.getShowIdFromXBMC(tvshow['tvdb_id'], tvshow['title'])
                if tvshow['idShow'] != -1:
                    li.setProperty('Available','true')
                if self.type != 'watchlist':
                    if 'watchlist' in tvshow:
                        if tvshow['watchlist']:
                            li.setProperty('Watchlist','true')
                self.getControl(TVSHOW_LIST).addItem(li)
            self.setFocus(self.getControl(TVSHOW_LIST))
            self.listUpdate()
        else:
            Debug("TVShowsWindow: Error: tvshows array is empty")
            self.close()

    def onFocus( self, controlId ):
        self.controlId = controlId

    def listUpdate(self):

        try:
            current = self.getControl(TVSHOW_LIST).getSelectedPosition()
        except TypeError:
            return # ToDo: error output

        try:
            self.getControl(BACKGROUND).setImage(self.tvshows[current]['images']['fanart'])
        except KeyError:
            Debug("KeyError for Backround")
        except TypeError:
            Debug("TypeError for Backround")
        try:
            self.getControl(TITLE).setLabel(self.tvshows[current]['title'])
        except KeyError:
            Debug("KeyError for Title")
            self.getControl(TITLE).setLabel("")
        except TypeError:
            Debug("TypeError for Title")
        try:
            self.getControl(OVERVIEW).setText(self.tvshows[current]['overview'])
        except KeyError:
            Debug("KeyError for Overview")
            self.getControl(OVERVIEW).setText("")
        except TypeError:
            Debug("TypeError for Overview")
        try:
            self.getControl(YEAR).setLabel("Year: " + str(self.tvshows[current]['year']))
        except KeyError:
            Debug("KeyError for Year")
            self.getControl(YEAR).setLabel("")
        except TypeError:
            Debug("TypeError for Year")
        try:
            self.getControl(RUNTIME).setLabel("Runtime: " + str(self.tvshows[current]['runtime']) + " Minutes")
        except KeyError:
            Debug("KeyError for Runtime")
            self.getControl(RUNTIME).setLabel("")
        except TypeError:
            Debug("TypeError for Runtime")
        try:
            self.getControl(TAGLINE).setLabel(str(self.tvshows[current]['tagline']))
        except KeyError:
            Debug("KeyError for Tagline")
            self.getControl(TAGLINE).setLabel("")
        except TypeError:
            Debug("TypeError for Tagline")
        try:
            self.getControl(RATING).setLabel("Rating: " + self.tvshows[current]['certification'])
        except KeyError:
            Debug("KeyError for Rating")
            self.getControl(RATING).setLabel("")
        except TypeError:
            Debug("TypeError for Rating")
        if self.type == 'trending':
            try:
                self.getControl(WATCHERS).setLabel(str(self.tvshows[current]['watchers']) + " people watching")
            except KeyError:
                Debug("KeyError for Watchers")
                self.getControl(WATCHERS).setLabel("")
            except TypeError:
                Debug("TypeError for Watchers")

    def showContextMenu(self):
        show = self.tvshows[self.getControl(TVSHOW_LIST).getSelectedPosition()]
        li = self.getControl(TVSHOW_LIST).getSelectedItem()
        options = []
        actions = []
        if self.type != 'watchlist':
            if 'watchlist' in show:
                if show['watchlist']:
                    options.append(__language__(137).encode( "utf-8", "ignore" ))
                    actions.append('unwatchlist')
                else:
                    options.append(__language__(136).encode( "utf-8", "ignore" ))
                    actions.append('watchlist')
            else:
                options.append(__language__(136).encode( "utf-8", "ignore" ))
                actions.append('watchlist')
        else:
            options.append(__language__(137).encode( "utf-8", "ignore" ))
            actions.append('unwatchlist')
        options.append(__language__(138).encode( "utf-8", "ignore" ))
        actions.append('rate')

        select = xbmcgui.Dialog().select(show['title'], options)
        if select != -1:
            Debug("Select: " + actions[select])
        if select == -1:
            Debug ("menu quit by user")
            return
        elif actions[select] == 'play':
            xbmcgui.Dialog().ok(__language__(200).encode( "utf-8", "ignore" ), __language__(152).encode( "utf-8", "ignore" ))
        elif actions[select] == 'unwatchlist':
            if utilities.removeTVShowsFromWatchlist([show]) == None:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(132).encode( "utf-8", "ignore" )) # Failed to remove from watch-list
            else:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(133).encode( "utf-8", "ignore" )) # Successfully removed from watch-list
                li.setProperty('Watchlist','false')
                show['watchlist'] = False
        elif actions[select] == 'watchlist':
            if utilities.addTVShowsToWatchlist([show]) == None:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(130).encode( "utf-8", "ignore" )) # Failed to added to watch-list
            else:
                utilities.notification(__language__(200).encode( "utf-8", "ignore" ), __language__(131).encode( "utf-8", "ignore" )) # Successfully added to watch-list
                li.setProperty('Watchlist','true')
                show['watchlist'] = True
        elif actions[select] == 'rate':
            rateShow = RateShowDialog("rate.xml", __settings__.getAddonInfo('path'), "Default")
            rateShow.initDialog(show['tvdb_id'], show['title'], show['year'], utilities.getShowRatingFromTrakt(show['tvdb_id'], show['title'], show['year']))
            rateShow.doModal()
            del rateShow

    def onAction(self, action):

        if action.getId() == 0:
            return
        if action.getId() in (ACTION_PARENT_DIRECTORY, ACTION_PREVIOUS_MENU):
            Debug("Closing TV Shows Window")
            self.close()
        elif action.getId() in (1, 2, 107):
            self.listUpdate()
        elif action.getId() == ACTION_SELECT_ITEM:
            pass # do something here ?
        elif action.getId() == ACTION_CONTEXT_MENU:
            self.showContextMenu()
        else:
            Debug("Uncaught action (tv shows): "+str(action.getId()))


class RateDialog(xbmcgui.WindowXMLDialog):
    """Base class implementing the methods that don't change in the rating dialogues"""
    def __init__(self, xml, fallback_path, defaultskinname="Default", forcefallback=False):
        super(RateDialog, self).__init__(xml, fallback_path, defaultskinname, forcefallback)

        self._id_to_rating_string = {
            RATE_LOVE_BTN: "love", RATE_HATE_BTN: "hate", RATE_ADVANCED_1_BTN: "1",
            RATE_ADVANCED_2_BTN: "2", RATE_ADVANCED_3_BTN: "3", RATE_ADVANCED_4_BTN: "4",
            RATE_ADVANCED_5_BTN: "5", RATE_ADVANCED_6_BTN: "6", RATE_ADVANCED_7_BTN: "7",
            RATE_ADVANCED_8_BTN: "8", RATE_ADVANCED_9_BTN: "9", RATE_ADVANCED_10_BTN: "10"
        }

        self._cur_rating = None
        self._control_id = None
        self._rating_type = utilities.getTraktRatingType()

    def initDialog(self, cur_rating):
        """Set up the generic current rating code"""
        self._cur_rating = cur_rating
        if self._cur_rating not in self._id_to_rating_string.values():
            self._cur_rating = None

    def onFocus(self, control_id):
        """Update currently selected item id"""
        self._control_id = control_id

    def onInit(self, header):
        """Set up the generic window code"""
        self.getControl(RATE_TITLE).setLabel(header)
        self.getControl(RATE_RATE_SHOW_BG).setVisible(False)
        self.getControl(RATE_RATE_SHOW_BTN).setVisible(False)
        self.getControl(RATE_CUR_NO_RATING).setEnabled(False)
        self.setFocus(self.getControl(RATE_SKIP_RATING))
        self._update_rated_button()

    def onClick(self, control_id, method):
        """Perform action when item clicked"""
        self._cur_rating = self._id_to_rating_string[control_id]
        self._update_rated_button()

        if control_id in (RATE_CUR_LOVE, RATE_CUR_HATE, RATE_CUR_ADVANCED_1, RATE_CUR_ADVANCED_2, RATE_CUR_ADVANCED_3, RATE_CUR_ADVANCED_4, RATE_CUR_ADVANCED_5, RATE_CUR_ADVANCED_6, RATE_CUR_ADVANCED_7, RATE_CUR_ADVANCED_8, RATE_CUR_ADVANCED_9, RATE_CUR_ADVANCED_10):
            self._cur_rating = "unrate"

        if self._cur_rating != "skip":
            method(self._cur_rating)

        self.close()

    def _update_rated_button(self):
        """Set the current rating button"""
        self.getControl(RATE_CUR_NO_RATING).setVisible(False if self._cur_rating != None else True)
        self.getControl(RATE_CUR_LOVE).setVisible(False if self._cur_rating != "love" else True)
        self.getControl(RATE_CUR_HATE).setVisible(False if self._cur_rating != "hate" else True)
        if self._rating_type == "advanced":
            self.getControl(RATE_CUR_ADVANCED_1).setVisible(False if self._cur_rating != "1" else True)
            self.getControl(RATE_CUR_ADVANCED_2).setVisible(False if self._cur_rating != "2" else True)
            self.getControl(RATE_CUR_ADVANCED_3).setVisible(False if self._cur_rating != "3" else True)
            self.getControl(RATE_CUR_ADVANCED_4).setVisible(False if self._cur_rating != "4" else True)
            self.getControl(RATE_CUR_ADVANCED_5).setVisible(False if self._cur_rating != "5" else True)
            self.getControl(RATE_CUR_ADVANCED_6).setVisible(False if self._cur_rating != "6" else True)
            self.getControl(RATE_CUR_ADVANCED_7).setVisible(False if self._cur_rating != "7" else True)
            self.getControl(RATE_CUR_ADVANCED_8).setVisible(False if self._cur_rating != "8" else True)
            self.getControl(RATE_CUR_ADVANCED_9).setVisible(False if self._cur_rating != "9" else True)
            self.getControl(RATE_CUR_ADVANCED_10).setVisible(False if self._cur_rating != "10" else True)

    def onAction(self, action):
        if action.getId() in (ACTION_PARENT_DIRECTORY, ACTION_PREVIOUS_MENU):
            Debug("Closing Dialog")
            self.close()


class RateMovieDialog(RateDialog):
    def __init__(self, xml, fallback_path, defaultskinname="Default", forcefallback=False):
        super(RateMovieDialog, self).__init__(xml, fallback_path, defaultskinname, forcefallback)
        self.imdbid = None
        self.title = None
        self.year = None

    def initDialog(self, imdbid, title, year, curRating):
        self.imdbid = imdbid
        self.title = title
        self.year = year
        super(RateMovieDialog, self).initDialog(curRating)

    def onInit(self):
        super(RateMovieDialog, self).onInit(__language__(142).encode("utf-8", "ignore"))

    def onClick(self, controlId):
        method = functools.partial(utilities.rateMovieOnTrakt, self.imdbid, self.title, self.year)
        super(RateMovieDialog, self).onClick(controlId, method)


class RateEpisodeDialog(RateDialog):
    def __init__(self, xml, fallback_path, defaultskinname="Default", forcefallback=False):
        super(RateEpisodeDialog, self).__init__(xml, fallback_path, defaultskinname, forcefallback)
        self.tvdbid = None
        self.title = None
        self.year = None
        self.season = None
        self.episode = None

    def initDialog(self, tvdbid, title, year, season, episode, curRating):
        self.tvdbid = tvdbid
        self.title = title
        self.year = year
        self.season = season
        self.episode = episode
        super(RateEpisodeDialog, self).initDialog(curRating)

    def onInit(self):
        super(RateEpisodeDialog, self).onInit(__language__(143).encode("utf-8", "ignore"))
        self.getControl(RATE_RATE_SHOW_BTN).setLabel(__language__(144).encode( "utf-8", "ignore" ))
        self.getControl(RATE_RATE_SHOW_BTN).setVisible(True)
        self.getControl(RATE_RATE_SHOW_BG).setVisible(True)

    def onClick(self, controlId):
        if controlId == RATE_RATE_SHOW_BTN:
            self.getControl(RATE_RATE_SHOW_BG).setVisible(False)
            self.getControl(RATE_RATE_SHOW_BTN).setVisible(False)
            self.setFocus(self.getControl(RATE_SKIP_RATING))

            if self._rating_type == "advanced":
                rateShow = RateShowDialog("rate_advanced.xml", __settings__.getAddonInfo('path'))
            else:
                rateShow = RateShowDialog("rate.xml", __settings__.getAddonInfo('path'))

            rateShow.initDialog(self.tvdbid, self.title, self.year, utilities.getShowRatingFromTrakt(self.tvdbid, self.title, self.year))
            rateShow.doModal()
            del rateShow
        else:
            method = functools.partial(utilities.rateEpisodeOnTrakt, self.tvdbid, self.title, self.year, self.season, self.episode)
            super(RateEpisodeDialog, self).onClick(controlId, method)


class RateShowDialog(RateDialog):
    def __init__(self, xml, fallback_path, defaultskinname="Default", forcefallback=False):
        super(RateShowDialog, self).__init__(xml, fallback_path, defaultskinname, forcefallback)
        self.tvdbid = None
        self.title = None
        self.year = None

    def initDialog(self, tvdbid, title, year, curRating):
        self.tvdbid = tvdbid
        self.title = title
        self.year = year
        super(RateShowDialog, self).initDialog(curRating)

    def onInit(self):
        super(RateShowDialog, self).onInit(__language__(145).encode("utf-8", "ignore"))

    def onClick(self, controlId):
        method = functools.partial(utilities.rateShowOnTrakt, self.tvdbid, self.title, self.year)
        super(RateShowDialog, self).onClick(controlId, method)

