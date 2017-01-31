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

from eolie.toolbar_actions import ToolbarActions
from eolie.toolbar_title import ToolbarTitle
from eolie.toolbar_end import ToolbarEnd


class Toolbar(Gtk.HeaderBar):
    """
        Eolie toolbar
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.HeaderBar.__init__(self)
        self.set_title("Eolie")
        self.__toolbar_actions = ToolbarActions()
        self.__toolbar_actions.show()
        self.__toolbar_title = ToolbarTitle()
        self.__toolbar_title.show()
        self.__toolbar_end = ToolbarEnd()
        self.__toolbar_end.show()
        self.pack_start(self.__toolbar_actions)
        self.set_custom_title(self.__toolbar_title)
        self.pack_end(self.__toolbar_end)

    @property
    def title(self):
        """
            Toolbar title
            @return ToolbarTitle
        """
        return self.__toolbar_title

    @property
    def actions(self):
        """
            Toolbar actions
            @return ToolbarActions
        """
        return self.__toolbar_actions

#######################
# PRIVATE             #
#######################
