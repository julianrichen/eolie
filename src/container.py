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
        self.__progress = Gtk.ProgressBar()
        self.__progress.get_style_context().add_class('progressbar')
        self.__progress.set_property('valign', Gtk.Align.START)
        overlay = Gtk.Overlay.new()
        overlay.add(self.__stack)
        overlay.add_overlay(self.__progress)
        overlay.show()
        self.add1(self.__stack_sidebar)
        self.add2(overlay)

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
        view.connect('map', self.__on_view_map)
        view.connect('notify::estimated-load-progress',
                     self.__on_estimated_load_progress)
        view.connect('load-changed', self.__on_load_changed)
        view.connect('button-press-event', self.__on_button_press)
        view.connect("notify::uri", self.__on_uri_changed)
        view.connect("notify::title", self.__on_title_changed)
        view.connect('enter-fullscreen', self.__on_enter_fullscreen)
        view.connect('leave-fullscreen', self.__on_leave_fullscreen)

        if uri != "about:blank":
            view.load_uri(uri)
        view.show()
        self.__stack_sidebar.add_child(view)
        if show:
            self.__stack.add(view)
            self.__stack.set_visible_child(view)
            self.__stack_sidebar.update_visible_child()

    def load_uri(self, uri):
        """
            Load uri in current view
            @param uri as str
        """
        if self.current is not None:
            self.current.load_uri(uri)

    @property
    def sidebar(self):
        """
            Get sidebar
            @return StackSidebar
        """
        return self.__stack_sidebar

    @property
    def views(self):
        """
            Get views
            @return views as [WebView]
        """
        return self.__stack.get_children()

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
    def __on_view_map(self, view):
        """
            Update window
            @param view as WebView
        """
        El().window.toolbar.title.set_uri(view.get_uri())
        if view.is_loading():
            self.__progress.show()
        else:
            self.__progress.hide()
            El().window.toolbar.title.set_title(view.get_title())

    def __on_button_press(self, widget, event):
        """
            Hide Titlebar popover
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        El().window.toolbar.title.hide_popover()

    def __on_estimated_load_progress(self, view, value):
        """
            Update progress bar
            @param view as WebView
            @param UNUSED
        """
        value = view.get_estimated_load_progress()
        self.__progress.set_fraction(value)

    def __on_uri_changed(self, view, uri):
        """
            Update uri
            @param view as WebView
            @param uri as str
        """
        if view == self.current:
            El().window.toolbar.title.set_uri(view.get_uri())

    def __on_title_changed(self, view, event):
        """
            Update title
            @param view as WebView
            @param title as str
        """
        if event.name != "title":
            return
        uri = view.get_uri()
        title = view.get_title()
        if view == self.current:
            if title:
                El().window.toolbar.title.set_title(title)
            else:
                El().window.toolbar.title.set_title(uri)
            El().window.toolbar.actions.set_actions(view)
        if title:
            El().history.add(title, uri)

    def __on_enter_fullscreen(self, view):
        """
            Hide sidebar (conflict with fs)
        """
        self.__stack_sidebar.hide()

    def __on_leave_fullscreen(self, view):
        """
            Show sidebar (conflict with fs)
        """
        self.__stack_sidebar.show()

    def __on_load_changed(self, view, event):
        """
            Update sidebar/urlbar
            @param view as WebView
            @param event as WebKit2.LoadEvent
        """
        if event == WebKit2.LoadEvent.STARTED:
            self.__progress.show()
        if event == WebKit2.LoadEvent.FINISHED:
            self.__progress.hide()
