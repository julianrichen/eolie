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


class DownloadsManager:
    """
        Downloads Manager
    """

    def __init__(self):
        """
            Init download manager
        """
        self.__downloads = []

    def add(self, download):
        """
            Add a download
            @param download as WebKit2.Download
        """
        self.__downloads.append(download)
        download.connect('finished', self.__on_finished)
        download.connect('failed', self.__on_failed)
        # download.connect('decide-destination', self.__on_decide_destination)

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
    def __on_finished(self, download):
        """
            @param download as WebKit2.Download
        """
        if download in self.__downloads:
            self.__downloads.remove(download)

    def __on_failed(self, download, error):
        """
            @param download as WebKit2.Download
            @param error as GLib.Error
        """
        print("DownloadManager::__on_failed:", error)
        if download in self.__downloads:
            self.__downloads.remove(download)
