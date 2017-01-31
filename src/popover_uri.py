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

from gi.repository import Gtk, Gdk, GObject, Gio, Pango

from eolie.define import El, ArtSize


class HistoryItem(GObject.GObject):
    title = GObject.Property(type=str,
                             default='')
    uri = GObject.Property(type=str,
                           default='')

    def __init__(self):
        GObject.GObject.__init__(self)


class HistoryRow(Gtk.ListBoxRow):
    """
        An history row
    """
    def __init__(self, item):
        """
            Init row
            @param item as HistoryItem
        """
        Gtk.ListBoxRow.__init__(self)
        self.__item = item
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_property('valign', Gtk.Align.CENTER)
        surface = El().art.get_artwork(item.get_property("uri"),
                                       "favicon",
                                       self.get_scale_factor(),
                                       ArtSize.FAVICON,
                                       ArtSize.FAVICON)
        favicon = Gtk.Image.new_from_surface(surface)
        favicon.set_size_request(ArtSize.FAVICON*2, -1)
        if surface is not None:
            del surface
        favicon.show()
        title = Gtk.Label.new(item.get_property("title"))
        title.set_ellipsize(Pango.EllipsizeMode.END)
        title.set_property('halign', Gtk.Align.START)
        title.set_hexpand(True)
        uri = Gtk.Label.new(item.get_property("uri"))
        uri.set_ellipsize(Pango.EllipsizeMode.END)
        uri.set_property('halign', Gtk.Align.END)
        uri.get_style_context().add_class('dim-label')
        uri.set_max_width_chars(40)
        grid.add(favicon)
        grid.add(title)
        grid.add(uri)
        grid.show_all()
        self.set_size_request(-1, 30)
        self.add(grid)

    @property
    def item(self):
        """
            Get item
            @return HistoryItem
        """
        return self.__item


class UriPopover(Gtk.Popover):
    """
        Show user bookmarks or history
    """

    def __init__(self):
        """
            Init popover
        """
        Gtk.Popover.__init__(self)
        self.set_modal(False)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/PopoverUri.ui')
        builder.connect_signals(self)
        self.__history_model = Gio.ListStore()
        self.__history_box = builder.get_object('history_box')
        self.__stack = builder.get_object('stack')
        self.__history_box.bind_model(self.__history_model,
                                      self.__on_history_create)
        self.add(builder.get_object('widget'))
        self.connect('map', self.__on_map)

    def set_history_text(self, search):
        """
            Set history model
            @param search as str
        """
        self.__history_model.remove_all()
        result = El().history.search(search)
        for (title, uri) in result:
            item = HistoryItem()
            item.set_property("title", title)
            item.set_property("uri", uri)
            self.__history_model.append(item)

    def send_event_to_history(self, event):
        """
            Forward event to history box
            @param event as Gdk.Eventg
        """
        rows = self.__history_box.get_children()
        if not rows:
            return
        selected = self.__history_box.get_selected_row()
        if event.keyval in [Gdk.KEY_Down, Gdk.KEY_Up]:
            # If nothing selected, select first row
            if selected is None:
                self.__history_box.select_row(rows[0])
            else:
                idx = -1 if event.keyval == Gdk.KEY_Up else 1
                for row in rows:
                    if row == selected:
                        break
                    idx += 1
                if idx < 0:
                    self.__history_box.select_row(rows[-1])
                elif idx >= len(rows):
                    self.__history_box.select_row(rows[0])
                else:
                    self.__history_box.select_row(rows[idx])
        elif event.keyval == Gdk.KEY_Return and selected is not None:
            selected.emit("activate")

#######################
# PROTECTED           #
#######################
    def _on_row_activated(self, listbox, row):
        """
            Got to uri
            @param listbox as Gtk.ListBox
            @param row as HistoryRow
        """
        El().window.container.current.load_uri(row.item.get_property("uri"))
        self.hide()

#######################
# PRIVATE             #
#######################
    def __on_map(self, widget):
        """
            Resize
            @param widget as Gtk.Widget
        """
        size = El().window.get_size()
        self.set_size_request(size[0]*0.5, size[1]*0.7)

    def __on_history_create(self, item):
        """
            Add child to history box
            @param item as HistoryItem
        """
        child = HistoryRow(item)
        return child
