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

from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, WebKit2
import cairo

from eolie.define import El


class SidebarChild(Gtk.ListBoxRow):
    """
        A Sidebar Child
    """
    __HEIGHT = 60

    def __init__(self, view):
        """
            Init child
            @param view as WebView
        """
        Gtk.ListBoxRow.__init__(self)
        self.__view = view
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/SidebarChild.ui')
        builder.connect_signals(self)
        self.__title = builder.get_object('title')
        self.__uri = builder.get_object('uri')
        self.__image = builder.get_object('image')
        self.__image_close = builder.get_object('image_close')
        self.__image_close.set_from_icon_name('web-browser-symbolic',
                                              Gtk.IconSize.DIALOG)
        self.__title.set_label("Empty page")
        self.add(builder.get_object('widget'))
        view.connect("notify::favicon", self.__on_notify_favicon)
        self.get_style_context().add_class('sidebar-item')

    @property
    def view(self):
        """
            Get linked view
            @return WebView
        """
        return self.__view

    def on_load_changed(self, view, event):
        """
            Update label/favicon
            @param view as WebView
            @parma event as WebKit2.LoadEvent
        """
        if event == WebKit2.LoadEvent.STARTED:
            self.__title.set_text(view.get_uri())
            El().navigation.emit('uri-changed', view.get_uri())
            self.__image.clear()
            self.__image_close.set_from_icon_name('web-browser-symbolic',
                                                  Gtk.IconSize.DIALOG)
        elif event == WebKit2.LoadEvent.FINISHED:
            title = view.get_title()
            if title is not None:
                self.__title.set_text(title)
            El().navigation.emit('title-changed', title)
            El().navigation.emit('uri-changed', view.get_uri())
            GLib.timeout_add(500, self.__set_preview)
            if view.get_favicon() is not None:
                GLib.timeout_add(500, self.__set_favicon)

#######################
# PROTECTED           #
#######################
    def _on_button_press(self, button, event):
        """
            Destroy self
        """
        self.destroy()

    def _on_enter_notify(self, eventbox, event):
        """
            Show close button
            @param eventbox as Gtk.EventBox
            @param event as Gdk.Event
        """
        self.__image_close.set_from_icon_name('close-symbolic',
                                              Gtk.IconSize.DIALOG)
        self.__image_close.get_style_context().add_class('sidebar-close')

    def _on_leave_notify(self, eventbox, event):
        """
            Show close button
            @param eventbox as Gtk.EventBox
            @param event as Gdk.Event
        """
        self.__image_close.get_style_context().remove_class('sidebar-close')
        self.__on_notify_favicon(self.__view, None)

#######################
# PRIVATE             #
#######################
    def __get_favicon(self, surface):
        """
            Resize surface to match favicon size
            @param surface as cairo.surface
        """
        if surface is None:
            return None
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0,
                                             surface.get_width(),
                                             surface.get_height())
        scaled = pixbuf.scale_simple(22, 22, GdkPixbuf.InterpType.BILINEAR)
        del pixbuf
        s = Gdk.cairo_surface_create_from_pixbuf(scaled,
                                                 self.get_scale_factor(), None)
        del scaled
        return s

    def __set_favicon(self):
        """
            Set favicon
        """
        surface = self.__get_favicon(self.__view.get_favicon())
        if surface is None:
            self.__image_close.set_from_icon_name('web-browser-symbolic',
                                                  Gtk.IconSize.DIALOG)
            return
        self.__image_close.set_from_surface(surface)
        del surface
        self.__image_close.get_style_context().remove_class('sidebar-close')
        self.__image_close.show()

    def __set_preview(self):
        """
            Set webpage preview
        """
        self.__view.get_snapshot(
                                WebKit2.SnapshotRegion.FULL_DOCUMENT,
                                WebKit2.SnapshotOptions.NONE,
                                None,
                                self.__on_snapshot)

    def __on_snapshot(self, view, result):
        """
            Set snapshot on main image
            @param view as WebView
            @param result as Gio.AsyncResult
        """
        try:
            snapshot = self.__view.get_snapshot_finish(result)
        except:
            return
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     self.get_allocated_width() - 10,
                                     self.__HEIGHT)
        context = cairo.Context(surface)
        context.set_source_surface(snapshot)
        factor = self.get_allocated_width() /\
            snapshot.get_width()
        context.scale(factor, factor)
        self.__view.draw(context)
        self.__image.set_from_surface(surface)
        del surface

    def __on_notify_favicon(self, view, pointer):
        """
            Set favicon
            @param view as WebView
            @param pointer as GParamPointer => unused
        """
        if view.get_favicon() is None:
            self.__image_close.set_from_icon_name('web-browser-symbolic',
                                                  Gtk.IconSize.DIALOG)
        else:
            self.__set_favicon()


class StackSidebar(Gtk.Grid):
    """
        Sidebar linked to a Gtk.Stack
    """
    def __init__(self, stack):
        """
            Init sidebar
            @param stack as Gtk.Stack
        """
        Gtk.Grid.__init__(self)
        self.__stack = stack
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.__scrolled = Gtk.ScrolledWindow()
        self.__scrolled.set_vexpand(True)
        self.__scrolled.show()
        self.__listbox = Gtk.ListBox.new()
        self.__listbox.set_activate_on_single_click(True)
        self.__listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.__listbox.show()
        self.__listbox.connect('row_activated', self.__on_row_activated)
        self.__scrolled.add(self.__listbox)
        self.add(self.__scrolled)

    def add_child(self, view):
        """
            Add child to sidebar
            @param view as WebView
        """
        child = SidebarChild(view)
        child.connect('destroy', self.__on_child_destroy)
        child.show()
        self.__listbox.add(child)

    def update_visible_child(self):
        """
            Mark current child as visible
            Unmark all others
        """
        visible = self.__stack.get_visible_child()
        for child in self.__listbox.get_children():
            if child.view == visible:
                child.get_style_context().add_class('sidebar-item-selected')
            else:
                child.get_style_context().remove_class('sidebar-item-selected')

    def on_load_changed(self, view, event):
        """
            Update child linked to view
            @param view as WebView
            @parma event as WebKit2.LoadEvent
        """
        for child in self.__listbox.get_children():
            if child.view == view:
                child.on_load_changed(view, event)
                break

#######################
# PRIVATE             #
#######################
    def __on_child_destroy(self, child):
        if len(self.__listbox.get_children()) == 0:
            El().window.new_web_view(True)
        child.view.destroy()

    def __on_row_activated(self, listbox, row):
        """
            Show wanted web view
            @param listbox as Gtk.ListBox
            @param row as SidebarChild
        """
        self.__stack.set_visible_child(row.view)
        self.update_visible_child()
