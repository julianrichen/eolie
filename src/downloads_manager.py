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

from gi.repository import GObject, GLib, Gio

from re import search


class DownloadsManager(GObject.GObject):
    """
        Downloads Manager
    """
    __gsignals__ = {
        'download-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        """
            Init download manager
        """
        GObject.GObject.__init__(self)
        self.__downloads = []

    def add(self, download):
        """
            Add a download
            @param download as WebKit2.Download
        """
        self.__downloads.append(download)
        download.connect('finished', self.__on_finished)
        download.connect('failed', self.__on_failed)
        self.emit('download-changed')
        download.connect('decide-destination', self.__on_decide_destination)

    def get_all(self):
        """
            Get all downloads
            @return [WebKit2.Download]
        """
        return self.__downloads

    def cancel(self):
        """
            Cancel all downloads
        """
        for download in self.__downloads:
            download.cancel()

#######################
# PRIVATE             #
#######################
    def __on_decide_destination(self, download, filename):
        """
            Modify destination if needed
            @param download as WebKit2.Download
            @param filename as str
        """
        directory = GLib.get_user_special_dir(
                                         GLib.UserDirectory.DIRECTORY_DOWNLOAD)
        directory_uri = GLib.filename_to_uri(directory, None)
        destination_uri = "%s/%s" % (directory_uri, filename)
        not_ok = True
        i = 1
        try:
            while not_ok:
                f = Gio.File.new_for_uri(destination_uri)
                if f.query_exists():
                    m = search('(.*)(\.[^\./]*$)', filename)
                    if m is not None:
                        root_filename = m.group(1)
                        extension = m.group(2)
                    else:
                        root_filename = filename
                        extension = ""
                    new_filename = "%s_%s%s" % (root_filename, i, extension)
                    destination_uri = "%s/%s" % (directory_uri, new_filename)
                else:
                    not_ok = False
        except:
            # Fallback to be sure
            destination_uri = "%s/%s" % (directory_uri, "@@" + filename)
        download.set_destination(destination_uri)

    def __on_finished(self, download):
        """
            @param download as WebKit2.Download
        """
        if download in self.__downloads:
            self.__downloads.remove(download)
        self.emit('download-changed')

    def __on_failed(self, download, error):
        """
            @param download as WebKit2.Download
            @param error as GLib.Error
        """
        print("DownloadManager::__on_failed:", error)
        if download in self.__downloads:
            self.__downloads.remove(download)
        self.emit('download-changed')
