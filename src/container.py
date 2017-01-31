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

from gi.repository import Gtk, WebKit2

from eolie.stacksidebar import StackSidebar
from eolie.define import El


class Container(Gtk.Paned):
    """
        Main Eolie view
    """

    def __init__(self):
        """
            Init container
        """
        Gtk.Paned.__init__(self)
        self.set_position(
            El().settings.get_value('paned-width').get_int32())
        self.__stack = Gtk.Stack()
        self.__stack.set_hexpand(True)
        self.__stack.set_vexpand(True)
        self.__stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.__stack.set_transition_duration(150)
        self.__stack.show()
        self.__stack_sidebar = StackSidebar(self.__stack)
        self.__stack_sidebar.show()
        self.add1(self.__stack_sidebar)
        self.add2(self.__stack)

    def add_web_view(self, uri, show):
        """
            Add a web view to container
            @param uri as str
            @param show as bool
        """
        from eolie.web_view import WebView
        if uri is None:
            uri = "about:blank"
        view = WebView()
        view.connect('load-changed', self.__on_load_changed)
        if uri != "about:blank":
            view.load_uri(uri)
        view.show()
        self.__stack_sidebar.add_child(view)
        if show:
            self.__stack.add(view)
            self.__stack.set_visible_child(view)
            El().window.toolbar.title.set_uri(uri)
            self.__stack_sidebar.update_visible_child()
        else:
            print("#FIXME")
            window = Gtk.OffscreenWindow.new()
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)
            scrolled.add(view)
            scrolled.set_size_request(1000, 1000)
            window.add(scrolled)
            window.show_all()

    def load_uri(self, uri):
        """
            Load uri in current view
            @param uri as str
        """
        if self.current is not None:
            self.current.load_uri(uri)

    @property
    def current(self):
        """
            Current view
            @return WebView
        """
        return self.__stack.get_visible_child()

#######################
# PRIVATE             #
#######################
    def __on_load_changed(self, view, event):
        """
            Update sidebar/urlbar
            @param view as WebView
            @param event as WebKit2.LoadEvent
        """
        self.__stack_sidebar.on_load_changed(view, event)
        if view == self.current:
            El().window.toolbar.title.set_uri(view.get_uri())
        if event == WebKit2.LoadEvent.FINISHED:
            El().history.add(view.get_title(), view.get_uri())
            if view == self.current:
                El().window.toolbar.actions.set_actions(view)
                El().window.toolbar.title.set_title(view.get_title())
