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

from gi.repository import Gtk, Gdk, GLib, GObject, Gio, Pango

from gettext import gettext as _

from eolie.define import El, ArtSize, BookmarksType


class Item(GObject.GObject):
    id = GObject.Property(type=int,
                          default=BookmarksType.URI)
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
        self.__eventbox = None
        Gtk.ListBoxRow.__init__(self)
        item_id = item.get_property("id")

        if item_id == BookmarksType.SEPARATOR:
            separator = Gtk.Separator()
            separator.show()
            self.add(separator)
            return

        uri = item.get_property("uri")
        title = item.get_property("title")
        self.__item = item
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_property('valign', Gtk.Align.CENTER)
        if item_id == BookmarksType.URI:
            surface = El().art.get_artwork(uri,
                                           "favicon",
                                           self.get_scale_factor(),
                                           ArtSize.FAVICON,
                                           ArtSize.FAVICON)
            favicon = Gtk.Image.new_from_surface(surface)
            if surface is None:
                favicon.set_from_icon_name("applications-internet",
                                           Gtk.IconSize.MENU)
            else:
                del surface
        else:
            if item_id == BookmarksType.POPULARS:
                icon_name = "starred-symbolic"
            elif item_id == BookmarksType.RECENTS:
                icon_name = "document-open-recent-symbolic"
            else:
                icon_name = "folder-symbolic"
            favicon = Gtk.Image.new_from_icon_name(icon_name,
                                                   Gtk.IconSize.MENU)
        favicon.show()
        title = Gtk.Label.new(title)
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
        self.__eventbox = Gtk.EventBox()
        self.__eventbox.add(grid)
        self.__eventbox.set_size_request(-1, 30)
        self.__eventbox.show()
        self.add(self.__eventbox)

    @property
    def eventbox(self):
        """
            Get eventbox
            @return Gtk.EventBox
        """
        return self.__eventbox

    @property
    def item(self):
        """
            Get item
            @return Item
        """
        return self.__item

#######################
# PRIVATE             #
#######################


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
        self.__scrolled_bookmarks = builder.get_object('scrolled_bookmarks')
        self.__history_model = Gio.ListStore()
        self.__history_box = builder.get_object('history_box')
        self.__stack = builder.get_object('stack')
        self.__stack.set_visible_child_name("bookmarks")
        self.__history_box.bind_model(self.__history_model,
                                      self.__on_item_create)
        self.__bookmarks_model = Gio.ListStore()
        self.__tags_model = Gio.ListStore()
        self.__tags = builder.get_object('tags')
        self.__tags_box = builder.get_object('tags_box')
        self.__tags_box.bind_model(self.__tags_model,
                                   self.__on_item_create)
        self.__bookmarks_box = builder.get_object('bookmarks_box')
        self.__bookmarks_box.bind_model(self.__bookmarks_model,
                                        self.__on_item_create)
        self.add(builder.get_object('widget'))
        self.connect('map', self.__on_map)

    def set_history_text(self, search):
        """
            Set history model
            @param search as str
        """
        self.__history_model.remove_all()
        self.__stack.set_visible_child_name("search")
        self.__set_history_text(search)

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
        if not self.__tags_box.get_children():
            static = [(BookmarksType.POPULARS,
                       _("Populars")),
                      (BookmarksType.RECENTS,
                       _("Recents")),
                      (BookmarksType.SEPARATOR, "")]
            for (tag_id, title) in static + El().bookmarks.get_tags():
                item = Item()
                item.set_property("id", tag_id)
                item.set_property("title", title)
                self.__tags_model.append(item)
        if self.__tags_box.get_children():
            self.__tags_box.select_row(self.__tags_box.get_children()[0])
            self.__set_bookmarks(BookmarksType.POPULARS)

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

#######################
# PRIVATE             #
#######################
    def __set_history_text(self, search):
        """
            Set history model
            @param search as str
        """
        result = El().history.search(search)
        for (title, uri) in result:
            item = Item()
            item.set_property("title", title)
            item.set_property("uri", uri)
            self.__history_model.append(item)

    def __set_bookmarks(self, tag_id):
        """
            Set bookmarks for tag id
            @param tag id as int
        """
        self.__bookmarks_model.remove_all()
        if tag_id == BookmarksType.POPULARS:
            items = El().bookmarks.get_populars()
        elif tag_id == BookmarksType.RECENTS:
            items = El().bookmarks.get_recents()
        else:
            items = El().bookmarks.get_bookmarks(tag_id)
        for (bookmark_id, title, uri) in items:
            item = Item()
            item.set_property("title", title)
            item.set_property("uri", uri)
            self.__bookmarks_model.append(item)

    def __handle_event(self, event, item):
        """
            Handle event (button press)
            @param event as Gdk.Event
            @param item as Item
        """
        uri = item.get_property("uri")
        item_id = item.get_property("id")
        if item_id == BookmarksType.URI:
            if event.button == 1:
                El().window.container.current.load_uri(uri)
            else:
                El().window.container.add_web_view(uri, True)
        else:
            self.__set_bookmarks(item_id)

    def __on_button_release(self, eventbox, event, item):
        """
            Got to uri
            @param eventbox as Gtk.EventBox
            @param event as Gdk.Event
            @param item as Item
        """
        if item.get_property("id") == BookmarksType.URI:
            El().window.toolbar.title.hide_popover()
        # Needed to not conflict with popover hidding
        GLib.idle_add(self.__handle_event, event, item)

    def __on_map(self, widget):
        """
            Resize
            @param widget as Gtk.Widget
        """
        size = El().window.get_size()
        self.set_size_request(size[0]*0.5, size[1]*0.7)
        self.__scrolled_bookmarks.set_size_request(size[1]*0.7*0.33, -1)

    def __on_item_create(self, item):
        """
            Add child to box
            @param item as Item
        """
        child = Row(item)
        if child.eventbox is not None:
            child.eventbox.connect('button-release-event',
                                   self.__on_button_release,
                                   item)
        return child
