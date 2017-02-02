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

from gi.repository import Soup, Gio, GLib

from urllib.parse import urlparse
import sqlite3
from time import time, sleep
from threading import Thread

from eolie.sqlcursor import SqlCursor


class DatabaseAdblock:
    """
        Eolie adblock db
    """
    if GLib.getenv("XDG_DATA_HOME") is None:
        __LOCAL_PATH = GLib.get_home_dir() + "/.local/share/eolie"
    else:
        __LOCAL_PATH = GLib.getenv("XDG_DATA_HOME") + "/eolie"
    DB_PATH = "%s/adblock.db" % __LOCAL_PATH

    __URIS = ["https://adaway.org/hosts.txt",
              "http://winhelp2002.mvps.org/hosts.txt",
              "http://hosts-file.net/ad_servers.txt",
              "https://pgl.yoyo.org/adservers/serverlist.php?"
              "hostformat=hosts&showintro=0&mimetype=plaintext"]

    # SQLite documentation:
    # In SQLite, a column with type INTEGER PRIMARY KEY
    # is an alias for the ROWID.
    # Here, we define an id INT PRIMARY KEY but never feed it,
    # this make VACUUM not destroy rowids...
    __create_adblock = '''CREATE TABLE adblock (
                                               id INTEGER PRIMARY KEY,
                                               dns TEXT NOT NULL,
                                               mtime INT NOT NULL
                                               )'''

    def __init__(self):
        """
            Create database tables or manage update if needed
        """
        self.__cancellable = Gio.Cancellable.new()
        f = Gio.File.new_for_path(self.DB_PATH)
        # Lazy loading if not empty
        self.__sleep = 0.5
        if not f.query_exists():
            try:
                self.__sleep = 0.1
                d = Gio.File.new_for_path(self.__LOCAL_PATH)
                if not d.query_exists():
                    d.make_directory_with_parents()
                # Create db schema
                with SqlCursor(self) as sql:
                    sql.execute(self.__create_adblock)
                    sql.commit()
            except Exception as e:
                print("DatabaseAdblock::__init__(): %s" % e)

    def update(self):
        """
            Update database
        """
        if Gio.NetworkMonitor.get_default().get_network_available():
            self.__mtime = int(time())
            self.__thread = Thread(target=self.__update)
            self.__thread.daemon = True
            self.__thread.start()

    def stop(self):
        """
            Stop update
        """
        self.__cancellable.cancel()
        self.__cancellable.reset()

    def is_blocked(self, uri):
        """
            Return True if uri is blocked
            @param uri as str
            @return bool
        """
        try:
            parse = urlparse(uri)
            with SqlCursor(self) as sql:
                result = sql.execute("SELECT mtime FROM adblock\
                                      WHERE dns=?", (parse.netloc,))
                v = result.fetchone()
                return v is not None
        except Exception as e:
            print("DatabaseAdblock::is_blocked():", e)
            return False

    def get_cursor(self):
        """
            Return a new sqlite cursor
        """
        try:
            c = sqlite3.connect(self.DB_PATH, 600.0)
            return c
        except:
            exit(-1)

#######################
# PRIVATE             #
#######################
    def __update(self):
        """
            Update database
        """
        result = ""
        try:
            for uri in self.__URIS:
                session = Soup.Session.new()
                request = session.request(uri)
                stream = request.send(self.__cancellable)
                bytes = bytearray(0)
                buf = stream.read_bytes(1024, self.__cancellable).get_data()
                while buf:
                    bytes += buf
                    buf = stream.read_bytes(
                                           1024, self.__cancellable).get_data()
                result = bytes.decode('utf-8')
                for line in result.split('\n'):
                    if self.__cancellable.is_cancelled():
                        raise IOError("Cancelled")
                    sleep(self.__sleep)
                    if line.startswith('#'):
                        continue
                    array = line.replace(
                                 ' ', '\t', 1).replace('\t', '@', 1).split('@')
                    if len(array) <= 1:
                        continue
                    dns = array[1].replace(
                                       ' ', '').replace('\r', '').split('#')[0]
                    # Update entry if exists, create else
                    with SqlCursor(self) as sql:
                        result = sql.execute("SELECT mtime FROM adblock\
                                              WHERE dns=?", (dns,))
                        v = result.fetchone()
                        if v is not None:
                            sql.execute("UPDATE adblock set mtime=?\
                                         WHERE dns=?", (self.__mtime, dns))
                        else:
                            sql.execute("INSERT INTO adblock\
                                              (dns, mtime)\
                                              VALUES (?, ?)",
                                        (dns, self.__mtime))
                        sql.commit()
            # Delete removed entries
            with SqlCursor(self) as sql:
                sql.execute("DELETE FROM adblock\
                             WHERE mtime!=?", (self.__mtime,))
        except Exception as e:
            print("DatabaseAdlbock:__update():", e)
