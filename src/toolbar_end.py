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
from eolie.popover_downloads import DownloadsPopover


class ProgressBar(Gtk.ProgressBar):
    """
        Simple progress bar with width contraint and event pass through
    """
    def __init__(self, parent):
        Gtk.ProgressBar.__init__(self)
        self.__parent = parent
        self.set_property('valign', Gtk.Align.END)

    def do_get_preferred_width(self):
        return (24, 24)


class ToolbarEnd(Gtk.Bin):
    """
        Toolbar end
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.Bin.__init__(self)
        self.__timeout_id = None
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/ToolbarEnd.ui')
        builder.connect_signals(self)
        self.__download_button = builder.get_object('download_button')
        eventbox = Gtk.EventBox()
        eventbox.connect('button-release-event', self.__on_event_release_event)
        eventbox.show()
        self.__progress = ProgressBar(builder.get_object('download_button'))
        if El().downloads_manager.get_all():
            self._progress.show()
        El().downloads_manager.connect('download-changed',
                                       self.__on_download_changed)
        eventbox.add(self.__progress)
        builder.get_object('overlay').add_overlay(eventbox)
        if El().settings.get_value('adblock'):
            builder.get_object(
                         'adblock_button').get_style_context().add_class('red')
        self.add(builder.get_object('end'))

#######################
# PROTECTED           #
#######################
    def _on_download_button_clicked(self, button):
        """
            Show download popover
            @param button as Gtk.Button
        """
        popover = DownloadsPopover()
        popover.set_relative_to(button)
        popover.show()

    def _on_adblock_button_clicked(self, button):
        """
            Switch add blocking on/off
            @param button as Gtk.Button
        """
        value = not El().settings.get_value('adblock')
        El().settings.set_value('adblock',
                                GLib.Variant('b', value))
        if value:
            button.get_style_context().add_class('red')
        else:
            button.get_style_context().remove_class('red')

#######################
# PRIVATE             #
#######################
    def __update_progress(self, downloads_manager):
        """
            Update progress
        """
        fraction = 0.0
        nb_downloads = 0
        for download in downloads_manager.get_all():
            nb_downloads += 1
            fraction += download.get_estimated_progress()
        if nb_downloads:
            self.__progress.set_fraction(fraction/nb_downloads)
        return True

    def __on_event_release_event(self, widget, event):
        """
            Forward event to button
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        self.__download_button.clicked()

    def __on_download_changed(self, downloads_manager):
        """
            Update progress bar
            @param downloads manager as DownloadsManager
        """
        if downloads_manager.get_all():
            if self.__timeout_id is None:
                self.__progress.show()
                self.__timeout_id = GLib.timeout_add(1000,
                                                     self.__update_progress,
                                                     downloads_manager)
        else:
            self.__progress.hide()
            GLib.source_remove(self.__timeout_id)
            self.__timeout_id = None
