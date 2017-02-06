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


class ToolbarEnd(Gtk.Bin):
    """
        Toolbar end
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.Bin.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/ToolbarEnd.ui')
        builder.connect_signals(self)
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
