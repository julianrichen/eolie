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

from eolie.define import El


class ToolbarTitle(Gtk.Bin):
    """
        Title toolbar
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.Bin.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/ToolbarTitle.ui')
        builder.connect_signals(self)
        self.add(builder.get_object('widget'))
        self.set_width(400)

    def set_width(self, width):
        """
            Set Gtk.Scale progress width
            @param width as int
        """
        self.set_property("width_request", width)

#######################
# PROTECTED           #
#######################
    def _on_activate(self, entry):
        """
            Go to url or search for words
            @param entry as Gtk.Entry
        """
        El().window.container.load_uri(entry.get_text())
#######################
# PRIVATE             #
#######################
