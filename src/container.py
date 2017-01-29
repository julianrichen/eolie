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

from gi.repository import Gtk

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
        self.__scrolled = Gtk.ScrolledWindow()
        self.__scrolled.set_hexpand(True)
        self.__scrolled.set_vexpand(True)
        self.__scrolled.show()
        self.__stack = Gtk.Stack()
        self.__stack.show()
        self.__scrolled.add(self.__stack)
        self.__stack_sidebar = StackSidebar(self.__stack)
        self.__stack_sidebar.show()
        self.add1(self.__stack_sidebar)
        self.add2(self.__scrolled)

    def add_web_view(self, uri=None):
        """
            Add a web view to container
            @param uri as str
        """
        from eolie.web_view import WebView
        view = WebView()
        view.show()
        self.__stack_sidebar.add_child(view)
        if uri is not None:
            view.load_uri(uri)
