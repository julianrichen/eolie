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

from gi.repository import Gtk, GLib

from eolie.define import El
from eolie.toolbar import Toolbar
from eolie.container import Container


class Window(Gtk.ApplicationWindow):
    """
        Main window
    """

    def __init__(self):
        """
            Init window
        """
        self.__timeout_configure = None
        Gtk.ApplicationWindow.__init__(self,
                                       application=El(),
                                       title="Eolie")

        self.__setup_content()
        self.setup_window()
        self.connect('destroy', self.__on_destroyed_window)
        self.connect('realize', self.__on_realize)
        self.connect('window-state-event', self.__on_window_state_event)
        self.connect('configure-event', self.__on_configure_event)
        self.__container.add_web_view("https://linuxfr.org")

    def setup_window(self):
        """
            Setup window position and size
        """
        self.__setup_pos()
        if El().settings.get_value('window-maximized'):
            self.maximize()

############
# Private  #
############
    def __setup_content(self):
        """
            Setup window content
        """
        self.set_default_icon_name('web-browser')
        vgrid = Gtk.Grid()
        vgrid.set_orientation(Gtk.Orientation.VERTICAL)
        vgrid.show()
        self.__toolbar = Toolbar()
        self.__toolbar.show()
        if El().prefers_app_menu():
            self.set_titlebar(self.__toolbar)
            self.__toolbar.set_show_close_button(True)
        else:
            vgrid.add(self.__toolbar)
        self.__container = Container()
        self.__container.show()
        vgrid.add(self.__container)
        self.add(vgrid)

    def __setup_pos(self):
        """
            Set window position
        """
        size_setting = El().settings.get_value('window-size')
        if len(size_setting) == 2 and\
           isinstance(size_setting[0], int) and\
           isinstance(size_setting[1], int):
            self.resize(size_setting[0], size_setting[1])
        position_setting = El().settings.get_value('window-position')
        if len(position_setting) == 2 and\
           isinstance(position_setting[0], int) and\
           isinstance(position_setting[1], int):
            self.move(position_setting[0], position_setting[1])

    def __on_configure_event(self, widget, event):
        """
            Delay event
            @param: widget as Gtk.Window
            @param: event as Gdk.Event
        """
        if self.__timeout_configure:
            GLib.source_remove(self.__timeout_configure)
            self.__timeout_configure = None
        if not self.is_maximized():
            self.__timeout_configure = GLib.timeout_add(
                                                   1000,
                                                   self.__save_size_position,
                                                   widget)

    def __save_size_position(self, widget):
        """
            Save window state, update current view content size
            @param: widget as Gtk.Window
        """
        self.__timeout_configure = None
        size = widget.get_size()
        El().settings.set_value('window-size',
                                GLib.Variant('ai', [size[0], size[1]]))

        position = widget.get_position()
        El().settings.set_value('window-position',
                                GLib.Variant('ai',
                                             [position[0], position[1]]))

    def __on_window_state_event(self, widget, event):
        """
            Save maximised state
        """
        El().settings.set_boolean('window-maximized',
                                  'GDK_WINDOW_STATE_MAXIMIZED' in
                                  event.new_window_state.value_names)

    def __on_realize(self, widget):
        """
            Run scanner on realize
            @param widget as Gtk.Widget
        """
        pass

    def __on_destroyed_window(self, widget):
        """
            Save paned widget width
            @param widget as unused, data as unused
        """
        return
        main_pos = self._paned_main_list.get_position()
        listview_pos = self._paned_list_view.get_position()
        listview_pos = listview_pos if listview_pos > 100 else 100
        El().settings.set_value('paned-mainlist-width',
                                GLib.Variant('i',
                                             main_pos))
        El().settings.set_value('paned-listview-width',
                                GLib.Variant('i',
                                             listview_pos))
