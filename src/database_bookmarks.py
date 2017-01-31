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

from eolie.utils import noaccents
from eolie.sqlcursor import SqlCursor


class DatabaseBookmarks:
    """
        Eolie bookmarks db
    """
    if GLib.getenv("XDG_DATA_HOME") is None:
        __LOCAL_PATH = GLib.get_home_dir() + "/.local/share/eolie"
    else:
        __LOCAL_PATH = GLib.getenv("XDG_DATA_HOME") + "/eolie"
    DB_PATH = "%s/bookmarks.db" % __LOCAL_PATH

    # SQLite documentation:
    # In SQLite, a column with type INTEGER PRIMARY KEY
    # is an alias for the ROWID.
    # Here, we define an id INT PRIMARY KEY but never feed it,
    # this make VACUUM not destroy rowids...
    __create_bookmarks = '''CREATE TABLE bookmarks (
                                               id INTEGER PRIMARY KEY,
                                               title TEXT NOT NULL,
                                               uri TEXT NOT NULL,
                                               tags TEXT NOT NULL,
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
                    sql.execute(self.__create_bookmarks)
                    sql.commit()
            except Exception as e:
                print("DatabaseBookmarks::__init__(): %s" % e)

    def add(self, title, uri, tags):
        """
            Add a new bookmark
            @param title as str
            @param uri as str
        """
        if not uri or not title:
            return
        with SqlCursor(self) as sql:
            sql.execute("INSERT INTO bookmarks\
                              (title, uri, tags, popularity)\
                              VALUES (?, ?, ?, ?)",
                        (title, uri, tags, 0))
            sql.commit()

    def get_id(self, uri):
        """
            Get id for uri
            @param uri as str
        """
        with SqlCursor(self) as sql:
            result = sql.execute("SELECT rowid\
                                  FROM bookmarks\
                                  WHERE uri=?", (uri,))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def get(self):
        """
            Get all bookmarks
            @return [(title, uri, tags)]
        """
        with SqlCursor(self) as sql:
            result = sql.execute("SELECT title, uri, tags\
                                  FROM bookmarks\
                                  ORDER BY popularity DESC, mtime DESC")
            return list(result)

    def import_firefox(self):
        """
            Mozilla Firefox importer
        """
        firefox_path = GLib.get_home_dir() + "/.mozilla/firefox/"
        d = Gio.File.new_for_path(firefox_path)
        infos = d.enumerate_children(
            'standard::name,standard::type',
            Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
            None)
        sqlite_path = None
        for info in infos:
            if info.get_file_type() == Gio.FileType.DIRECTORY:
                f = Gio.File.new_for_path(firefox_path +
                                          info.get_name() + "/places.sqlite")
                if f.query_exists():
                    sqlite_path = f.get_path()
                    break
        if sqlite_path is not None:
            c = sqlite3.connect(sqlite_path, 600.0)
            result = c.execute("SELECT bookmarks.title,\
                                       moz_places.url,\
                                       tags.title\
                                FROM moz_bookmarks AS bookmarks,\
                                     moz_bookmarks AS tags,\
                                     moz_places\
                                WHERE bookmarks.fk=moz_places.id\
                                AND bookmarks.type=1\
                                AND tags.id=bookmarks.parent")
            for (title, uri,  tags) in list(result):
                rowid = self.get_id(uri)
                if rowid is None:
                    self.add(title, uri, tags)

    def search(self, search):
        """
            Search string in db (uri and title)
            @param search as str
        """
        with SqlCursor(self) as sql:
            filter = '%' + search + '%'
            result = sql.execute("SELECT title, uri\
                                  FROM bookmarks\
                                  WHERE title LIKE ?\
                                   OR uri LIKE ?\
                                  ORDER BY popularity DESC, mtime DESC",
                                 (filter, filter))
            return list(result)

    def get_cursor(self):
        """
            Return a new sqlite cursor
        """
        try:
            c = sqlite3.connect(self.DB_PATH, 600.0)
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
            print("DatabaseBookmarks::drop_db():", e)

#######################
# PRIVATE             #
#######################
