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

from gi.repository import WebKit2, GLib

from eolie.define import El


class WebView(WebKit2.WebView):
    """
        WebKit view
    """

    def __init__(self):
        """
            Init view
        """
        WebKit2.WebView.__init__(self)
        self.__scroll_timeout_id = None
        self.__loaded_uri = ""
        settings = self.get_settings()
        settings.set_property("allow-file-access-from-file-urls",
                              False)
        settings.set_property("auto-load-images", True)
        settings.set_property("enable-java", False)
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
        self.set_zoom_level(1.2)
        self.show()
        self.connect('decide-policy', self.__on_decide_policy)
        self.connect('scroll-event', self.__on_scroll_event)

    def load_uri(self, uri):
        """
            Load uri
            @param uri as str
        """
        self.__loaded_uri = uri
        if not uri.startswith("http://") and not uri.startswith("https://"):
            uri = "http://" + uri
        WebKit2.WebView.load_uri(self, uri)

    @property
    def loaded_uri(self):
        """
            Return loaded uri (This is not current uri!)
            @return str
        """
        return self.__loaded_uri

#######################
# PRIVATE             #
#######################
    def __update_snapshot(self):
        """
            Update snapshot
        """
        self.__scroll_timeout_id = None
        El().window.container.sidebar.update_preview(self)

    def __on_scroll_event(self, view, event):
        """
            Update snapshot
        """
        if self.__scroll_timeout_id is not None:
            GLib.source_remove(self.__scroll_timeout_id)
        self.__scroll_timeout_id = GLib.timeout_add(1000,
                                                    self.__update_snapshot)

    def __on_decide_policy(self, view, decision, decision_type):
        """
            Navigation policy
            @param view as WebKit2.WebView
            @param decision as WebKit2.NavigationPolicyDecision
            @param decision_type as WebKit2.PolicyDecisionType
            @return bool
        """
        # Always accept response
        if decision_type == WebKit2.PolicyDecisionType.RESPONSE:
            decision.use()
            return False

        uri = decision.get_navigation_action().get_request().get_uri()
        if decision.get_mouse_button() == 0:
            decision.use()
            return False
        elif decision.get_mouse_button() == 1:
            self.__loaded_uri = uri
            decision.use()
            return False
        else:
            El().window.container.add_web_view(uri, True)
            decision.ignore()
            return True
