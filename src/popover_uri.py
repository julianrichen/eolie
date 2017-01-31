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


class Item(GObject.GObject):
    title = GObject.Property(type=str,
                             default='')
    uri = GObject.Property(type=str,
                           default='')

    def __init__(self):
        GObject.GObject.__init__(self)


class Row(Gtk.ListBoxRow):
    """
        A row
    """
    def __init__(self, item):
        """
            Init row
            @param item as Item
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
            @return Item
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
                                      self.__on_item_create)
        self.__bookmarks_model = Gio.ListStore()
        self.__bookmarks_tree = builder.get_object('bookmarks_tree')
        self.__bookmarks_tags = builder.get_object('bookmarks_tags')
        self.__bookmarks_box = builder.get_object('bookmarks_box')
        self.__bookmarks_box.bind_model(self.__bookmarks_model,
                                        self.__on_item_create)
        # self.__bookmarks_tree.set_row_separator_func(self.__row_separator_func)
        self.__renderer0 = Gtk.CellRendererText()
        self.__renderer0.set_property('ellipsize-set', True)
        self.__renderer0.set_property('ellipsize', Pango.EllipsizeMode.END)
        self.__renderer1 = Gtk.CellRendererPixbuf()
        # 16px for Gtk.IconSize.MENU
        self.__renderer1.set_fixed_size(16, -1)
        column = Gtk.TreeViewColumn('')
        column.set_expand(True)
        column.pack_start(self.__renderer0, True)
        column.add_attribute(self.__renderer0, 'text', 1)
        column.pack_start(self.__renderer1, False)
        column.add_attribute(self.__renderer1, 'icon-name', 2)
        self.__bookmarks_tree.append_column(column)
        self.__bookmarks_tree.set_property('has_tooltip', True)
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
            item = Item()
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
    def _on_selection_changed(self, selection):
        """
            Update listbox
            @param view as Gtk.TreeSelection
        """
        (store, iterator) = self.__bookmarks_tree.get_selection(
                                                               ).get_selected()
        if iterator is None:
            return
        tag_id = self.__bookmarks_tags.get_value(iterator, 0)
        self.__set_bookmarks(tag_id)

    def _on_history_map(self, widget):
        """
            Init history
            @param widget as Gtk.Widget
        """
        self.set_history_text("")

    def _on_bookmarks_map(self, widget):
        """
            Init bookmarks
            @param widget as Gtk.Widget
        """
        if len(self.__bookmarks_tags) == 0:
            for (tag_id, title) in El().bookmarks.get_tags():
                self.__bookmarks_tags.append([tag_id, title, ""])

    def _on_history_unmap(self, widget):
        """
            Clear history
            @param widget as Gtk.Widget
        """
        pass

    def _on_bookmarks_unmap(self, widget):
        """
            Clear bookmarks
            @param widget as Gtk.Widget
        """
        pass

    def _on_row_activated(self, listbox, row):
        """
            Got to uri
            @param listbox as Gtk.ListBox
            @param row as Row
        """
        El().window.container.current.load_uri(row.item.get_property("uri"))
        self.hide()

#######################
# PRIVATE             #
#######################
    def __set_bookmarks(self, tag_id):
        """
            Set bookmarks for tag id
            @param tag id as int
        """
        self.__bookmarks_model.remove_all()
        for (bookmark_id, title, uri) in El().bookmarks.get_bookmarks(tag_id):
            item = Item()
            item.set_property("title", title)
            item.set_property("uri", uri)
            self.__bookmarks_model.append(item)

    def __on_map(self, widget):
        """
            Resize
            @param widget as Gtk.Widget
        """
        size = El().window.get_size()
        self.set_size_request(size[0]*0.5, size[1]*0.7)

    def __on_item_create(self, item):
        """
            Add child to box
            @param item as Item
        """
        child = Row(item)
        return child
