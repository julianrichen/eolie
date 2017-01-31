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

from gi.repository import GLib, Gio

import sqlite3
from time import time

from eolie.utils import noaccents
from eolie.localized import LocalizedCollation
from eolie.sqlcursor import SqlCursor


class DatabaseHistory:
    """
        Eolie history db
    """
    if GLib.getenv("XDG_DATA_HOME") is None:
        __LOCAL_PATH = GLib.get_home_dir() + "/.local/share/eolie"
    else:
        __LOCAL_PATH = GLib.getenv("XDG_DATA_HOME") + "/eolie"
    DB_PATH = "%s/history.db" % __LOCAL_PATH

    # SQLite documentation:
    # In SQLite, a column with type INTEGER PRIMARY KEY
    # is an alias for the ROWID.
    # Here, we define an id INT PRIMARY KEY but never feed it,
    # this make VACUUM not destroy rowids...
    __create_history = '''CREATE TABLE history (
                                               id INTEGER PRIMARY KEY,
                                               title TEXT NOT NULL,
                                               uri TEXT NOT NULL,
                                               mtime INT NOT NULL,
                                               popularity INT NOT NULL
                                               )'''

    def __init__(self):
        """
            Create database tables or manage update if needed
        """
        f = Gio.File.new_for_path(self.DB_PATH)
        if not f.query_exists():
            try:
                d = Gio.File.new_for_path(self.__LOCAL_PATH)
                if not d.query_exists():
                    d.make_directory_with_parents()
                # Create db schema
                with SqlCursor(self) as sql:
                    sql.execute(self.__create_history)
                    sql.commit()
            except Exception as e:
                print("DatabaseHistory::__init__(): %s" % e)

    def add(self, title, uri, mtime=None):
        """
            Add a new entry to history, if exists, update it
            @param title as str
            @param uri as str
            @param mtime as int
        """
        if not uri:
            return
        if title is None:
            title = ""
        if mtime is None:
            mtime = int(time())
        with SqlCursor(self) as sql:
            result = sql.execute("SELECT popularity FROM history\
                                  WHERE uri=?", (uri,))
            v = result.fetchone()
            if v is not None:
                sql.execute("UPDATE history set mtime=?, popularity=?\
                             WHERE uri=?", (int(time()), v[0]+1, uri))
            else:
                sql.execute("INSERT INTO history\
                                  (title, uri, mtime, popularity)\
                                  VALUES (?, ?, ?, ?)",
                            (title, uri, mtime, 0))
            sql.commit()

    def search(self, search):
        """
            Search string in db (uri and title)
            @param search as str
        """
        with SqlCursor(self) as sql:
            filter = '%' + search + '%'
            result = sql.execute("SELECT title, uri\
                                  FROM history\
                                  WHERE title LIKE ?\
                                   OR uri LIKE ?\
                                  ORDER BY mtime DESC",
                                 (filter, filter))
            return list(result)

    def get_cursor(self):
        """
            Return a new sqlite cursor
        """
        try:
            c = sqlite3.connect(self.DB_PATH, 600.0)
            c.create_collation('LOCALIZED', LocalizedCollation())
            c.create_function("noaccents", 1, noaccents)
            return c
        except:
            exit(-1)

    def drop_db(self):
        """
            Drop database
        """
        try:
            f = Gio.File.new_for_path(self.DB_PATH)
            f.trash()
        except Exception as e:
            print("DatabaseHistory::drop_db():", e)

#######################
# PRIVATE             #
#######################
