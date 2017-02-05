# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Soup


class Search:
    """
        Eolie search engines
    """
    # https://ca.search.yahoo.com/sugg/
    # ff?command={%22llinux%22}&output=fxjson&appid=fd
    __ENGINES = {
        'Google': [
            'https://www.google.fr/search?q=%s&ie=utf-8&oe=utf-8',
            'https://www.google.com/complete/search?client=firefox&q={"%s"}'
            ]
        }

    def __init__(self):
        """
            Init toolbar
        """
        self.update_default_engine()

    def update_default_engine(self):
        """
            Update default engine based on user settings
        """
        wanted = "Google"
        for engine in self.__ENGINES:
            if engine == wanted:
                self.__search = self.__ENGINES[engine][0]
                self.__keywords = self.__ENGINES[engine][1]
                break

    def get_search_uri(self, words):
        """
            Return search uri for words
            @param words as str
            @return str
        """
        return self.__search % words

    def get_keywords(self, words, cancellable):
        """
            Get keywords for words
            @param words as str
            @param cancellable as Gio.Cancellable
            @return [str]
        """
        try:
            uri = self.__keywords % words
            session = Soup.Session.new()
            request = session.request(uri)
            stream = request.send(cancellable)
            bytes = bytearray(0)
            buf = stream.read_bytes(1024, cancellable).get_data()
            while buf:
                bytes += buf
                buf = stream.read_bytes(1024, cancellable).get_data()
            string = bytes.decode('unicode_escape')
            # format: '["{"words"}",["result1","result2"]]'
            keywords = string.replace('[', '').replace(']', '').split(',')[1:]
            return keywords
        except Exception as e:
            print("Search::get_keywords():", e)
            return []

    def is_search(self, string):
        """
            Return True is string is a search string
            @param string as str
            @return bool
        """
        # String contains space, not an uri
        search = string.find(" ") != -1
        if not search:
            # String contains dot, is an uri
            search = string.find(".") == -1
        return search

#######################
# PRIVATE             #
#######################
