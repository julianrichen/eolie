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

from eolie.define import El


class SidebarChild(Gtk.ListBoxRow):
    """
        A Sidebar Child
    """
    def __init__(self, webview=None):
        """
            Init child
            @param web as WebKit2.WebView
        """
        Gtk.ListBoxRow.__init__(self)
        self.__webview = None
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/SidebarChild.ui')
        self.__title = builder.get_object('title')
        self.__uri = builder.get_object('uri')
        self.__image = builder.get_object('image')
        self.__title.set_label("Empty page")
        self.add_webview(webview)
        self.add(builder.get_object('widget'))

    def add_webview(self, webview):
        """
            Add a webview
            Do nothing if already exists
            @param webview as WebKit2.WebView
        """
        if self.__webview is None and webview is not None:
            webview.connect('load-changed', self.__on_load_changed)
            self.__webview = webview
            self.__image.set_from_icon_name('close-symbolic',
                                            Gtk.IconSize.MENU)

#######################
# PRIVATE             #
#######################
    def __on_load_changed(self, view, event):
        """
            Update label
            @param view as WebKit2.WebView
            @parma event as WebKit2.LoadEvent
        """
        if event == WebKit2.LoadEvent.STARTED:
            self.__uri.set_text(view.get_uri())
            El().navigation.emit('uri-changed', view.get_uri())
        elif event == WebKit2.LoadEvent.FINISHED:
            self.__title.set_text(view.get_title())
            El().navigation.emit('title-changed', view.get_title())
            if view.get_favicon() is None:
                view.connect("notify::favicon", self.__on_notify_favicon)
            else:
                self.__image.set_from_surface(view.get_favicon())

    def __on_notify_favicon(self, view, pointer):
        """
            Set favicon
            @param view as WebKit2.WebView
            @param pointer as GParamPointer
        """
        if view.get_favicon() is None:
            self.__image.set_from_icon_name('close-symbolic',
                                            Gtk.IconSize.MENU)
        else:
            self.__close.set_from_surface(view.get_favicon())


class StackSidebar(Gtk.Grid):
    """
        Sidebar linked to a Gtk.Stack
    """
    def __init__(self, stack):
        """
            Init sidebar
            @param stack as Gtk.Stack
        """
        Gtk.Grid.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.__scrolled = Gtk.ScrolledWindow()
        self.__scrolled.set_vexpand(True)
        self.__scrolled.show()
        self.__listbox = Gtk.ListBox.new()
        self.__listbox.show()
        self.__scrolled.add(self.__listbox)
        self.add(self.__scrolled)
        stack.connect('add', self.__on_stack_add)

#######################
# PRIVATE             #
#######################
    def __on_stack_add(self, stack, widget):
        """
            Add child to sidebar
            @param stack as Gtk.Stack
            @param widget as Gtk.Widget
        """
        child = SidebarChild(widget)
        child.show()
        self.__listbox.add(child)
