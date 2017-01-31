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


class ToolbarActions(Gtk.Bin):
    """
        Actions toolbar
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.Bin.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/ToolbarActions.ui')
        builder.connect_signals(self)

        self.add(builder.get_object('actions'))

        self.__back = builder.get_object('back_button')
        self.__forward = builder.get_object('forward_button')

    def set_actions(self, view):
        """
            Set available actions based on view
            @param view as WebView
        """
        self.__back.set_sensitive(view.can_go_back())
        self.__forward.set_sensitive(view.can_go_forward())

#######################
# PROTECTED           #
#######################
    def _on_back_button_clicked(self, button):
        """
            Go backward on current view
            @param button as Gtk.Button
        """
        El().window.container.current.go_back()

    def _on_forward_button_clicked(self, button):
        """
            aa
            @param button as Gtk.Button
        """
        El().window.container.current.go_forward()

    def _on_new_button_clicked(self, button):
        """
            Add a new web view
            @param button as Gtk.Button
        """
        El().window.new_web_view(True)
