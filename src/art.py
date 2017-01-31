# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# Copyright (c) 2013 Vadim Rutkovsky <vrutkovs@redhat.com>
# Copyright (c) 2013 Arnel A. Borja <kyoushuu@yahoo.com>
# Copyright (c) 2013 Seif Lotfy <seif@lotfy.com>
# Copyright (c) 2013 Guillaume Quintard <guillaume.quintard@gmail.com>
# Copyright (c) 2013 Lubosz Sarnecki <lubosz@gmail.com>
# Copyright (c) 2013 Sai Suman Prayaga <suman.sai14@gmail.com>
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

from gi.repository import Gdk, GdkPixbuf, Gio, GLib

from urllib.parse import urlparse


class Art:
    """
        Base art manager
    """
    if GLib.getenv("XDG_CACHE_HOME") is None:
        __CACHE_PATH = GLib.get_home_dir() + "/.cache/eolie"
    else:
        __CACHE_PATH = GLib.getenv("XDG_CACHE_HOME") + "/eolie"

    def __init__(self):
        """
            Init base art
        """
        self.__create_cache()

    def save_artwork(self, uri, surface, suffix):
        """
            Save artwork for uri with suffix
            @param uri as str
            @param surface as cairo.surface
            @param suffix as str
        """
        escaped = GLib.uri_escape_string(self.__strip_uri(uri), None, False)
        filepath = "%s/%s_%s.png" % (self.__CACHE_PATH, escaped, suffix)
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0,
                                             surface.get_width(),
                                             surface.get_height())
        pixbuf.savev(filepath, "png", [None], [None])
        del pixbuf

    def get_artwork(self, uri, suffix, scale_factor, width, heigth):
        """
            @param uri as str
            @param suffix as str
            @param scale factor as int
            @param width as int
            @param height as int
            @return cairo.surface
        """
        escaped = GLib.uri_escape_string(self.__strip_uri(uri), None, False)
        filepath = "%s/%s_%s.png" % (self.__CACHE_PATH, escaped, suffix)
        f = Gio.File.new_for_path(filepath)
        if f.query_exists():
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filepath,
                                                             width,
                                                             heigth,
                                                             True)
            surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf,
                                                           scale_factor, None)
            del pixbuf
            return surface
        return None

#######################
# PROTECTED           #
#######################

#######################
# PRIVATE             #
#######################
    def __strip_uri(self, uri):
        """
            Remove prefix from uri
            @param uri as str
            @return uri as str
        """
        parsed = urlparse(uri)
        scheme = "%s://" % parsed.scheme
        return parsed.geturl().replace(scheme, '', 1)

    def __create_cache(self):
        """
            Create cache dir
        """
        d = Gio.File.new_for_path(self.__CACHE_PATH)
        if not d.query_exists():
            try:
                d.make_directory_with_parents()
            except:
                print("Can't create %s" % self.__CACHE_PATH)
