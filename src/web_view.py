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

from gi.repository import WebKit2


class WebView(WebKit2.WebView):
    """
        WebKit view
    """

    def __init__(self):
        """
            Init view
        """
        WebKit2.WebView.__init__(self)
        settings = self.get_settings()
        settings.set_property("allow-file-access-from-file-urls",
                              False)
        settings.set_property("auto-load-images", True)
        settings.set_property("enable-java", True)
        settings.set_property("enable-javascript", True)
        settings.set_property("enable-media-stream", True)
        settings.set_property("enable-mediasource", True)
        settings.set_property("enable-offline-web-application-cache", True)
        settings.set_property("enable-page-cache", True)
        settings.set_property("enable-plugins", True)
        settings.set_property("enable-resizable-text-areas", True)
        settings.set_property("enable-smooth-scrolling", True)
        settings.set_property("enable-webaudio", True)
        settings.set_property("enable-webgl", True)
        settings.set_property("javascript-can-access-clipboard", True)
        settings.set_property("javascript-can-open-windows-automatically",
                              True)
        settings.set_property("media-playback-allows-inline", True)
        self.set_settings(settings)
        self.show()

    def load_uri(self, uri):
        """
            Load uri
            @param uri as str
        """
        if not uri.startswith("http://") or not uri.startswith("https://"):
            uri = "http://" + uri
        WebKit2.WebView.load_uri(self, uri)

#######################
# PRIVATE             #
#######################
