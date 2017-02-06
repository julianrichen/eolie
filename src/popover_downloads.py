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

from gi.repository import Gtk, GLib, Gio, Pango

from eolie.define import El


class Row(Gtk.ListBoxRow):
    """
        A row
    """
    def __init__(self, download):
        """
            Init row
            @param download as WebKit2.Download
        """
        Gtk.ListBoxRow.__init__(self)
        self.__download = download
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/RowDownload.ui')
        builder.connect_signals(self)
        filename = GLib.filename_from_uri(download.get_destination())
        if filename is not None:
            builder.get_object('label').set_label(
                                         GLib.path_get_basename(filename[0]))
            builder.get_object('path').set_label(filename[0])
        else:
            builder.get_object('label').set_label(download.get_destination())
            builder.get_object('label').set_ellipsize(
                                                   Pango.EllipsizeMode.START)
        self.__progress = builder.get_object('progress')
        self.__progress.set_fraction(download.get_estimated_progress())
        self.__stop_button = builder.get_object('stop_button')
        download.connect('finished', self.__on_finished)
        download.connect('received-data', self.__on_received_data)
        download.connect('failed', self.__on_failed)
        self.add(builder.get_object('row'))

#######################
# PROTECTED           #
#######################
    def _on_cancel_button_clicked(self, button):
        """
            Cancel download
            @param button as Gtk.Button
        """
        self.__download.cancel()
        self.destroy()

#######################
# PRIVATE             #
#######################
    def __on_received_data(self, download, length):
        """
            @param download as WebKit2.Download
            @param length as int
        """
        self.__progress.set_fraction(download.get_estimated_progress())

    def __on_finished(self, download):
        """
            @param download as WebKit2.Download
        """
        self.__stop_button.hide()
        self.__progress.hide()

    def __on_failed(self, download, error):
        """
            @param download as WebKit2.Download
            @param error as GLib.Error
        """
        self.__stop_button.hide()
        self.__progress.hide()


class DownloadsPopover(Gtk.Popover):
    """
        Show current downloads
    """

    def __init__(self):
        """
            Init popover
        """
        Gtk.Popover.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/PopoverDownloads.ui')
        builder.connect_signals(self)
        self.__model = Gio.ListStore()
        self.__listbox = builder.get_object('downloads_box')
        self.__listbox.set_placeholder(builder.get_object('placeholder'))
        self.__listbox.bind_model(self.__model,
                                  self.__on_item_create)
        self.__scrolled = builder.get_object('scrolled')
        self.add(builder.get_object('widget'))
        self.connect('map', self.__on_map)
        for download in El().downloads_manager.get_all():
            self.__model.append(download)

#######################
# PROTECTED           #
#######################

#######################
# PRIVATE             #
#######################
    def __on_map(self, widget):
        """
            Resize
            @param widget as Gtk.Widget
        """
        self.set_size_request(400, -1)

    def __on_child_size_allocate(self, widget, allocation=None):
        """
            Update popover height request
            @param widget as Gtk.Widget
            @param allocation as Gdk.Rectangle
        """
        height = 0
        for child in self.__listbox.get_children():
            height += allocation.height
        size = El().active_window.get_size()
        if height > size[1] * 0.6:
            height = size[1] * 0.6
        self.__scrolled.set_size_request(400, height)

    def __on_item_create(self, download):
        """
            Add child to box
            @param download as WebKit2.Download
        """
        child = Row(download)
        child.connect('size-allocate', self.__on_child_size_allocate)
        return child
