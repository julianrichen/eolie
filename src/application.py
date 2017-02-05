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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
gi.require_version('Soup', '2.4')
from gi.repository import Gtk, Gio, GLib, Gdk, WebKit2

from gettext import gettext as _

from eolie.settings import Settings
from eolie.window import Window
from eolie.art import Art
from eolie.database_history import DatabaseHistory
from eolie.database_bookmarks import DatabaseBookmarks
from eolie.search import Search


class Application(Gtk.Application):
    """
        Eolie application:
    """

    if GLib.getenv("XDG_DATA_HOME") is None:
        __LOCAL_PATH = GLib.get_home_dir() + "/.local/share/eolie"
    else:
        __LOCAL_PATH = GLib.getenv("XDG_DATA_HOME") + "/eolie"
    __COOKIES_PATH = "%s/cookies.db" % __LOCAL_PATH
    __FAVICONS_PATH = "%s/favicons" % __LOCAL_PATH

    def __init__(self):
        """
            Create application
        """
        Gtk.Application.__init__(
                            self,
                            application_id='org.gnome.Eolie',
                            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.set_property('register-session', True)
        # Ideally, we will be able to delete this once Flatpak has a solution
        # for SSL certificate management inside of applications.
        if GLib.file_test("/app", GLib.FileTest.EXISTS):
            paths = ["/etc/ssl/certs/ca-certificates.crt",
                     "/etc/pki/tls/cert.pem",
                     "/etc/ssl/cert.pem"]
            for path in paths:
                if GLib.file_test(path, GLib.FileTest.EXISTS):
                    GLib.setenv('SSL_CERT_FILE', path, True)
                    break

        self.window = None
        self.debug = False
        self.cursors = {}
        GLib.set_application_name('Eolie')
        GLib.set_prgname('eolie')
        self.connect('activate', self.__on_activate)
        self.register(None)
        if self.get_is_remote():
            Gdk.notify_startup_complete()

    def init(self):
        """
            Init main application
        """
        self.__is_fs = False
        if Gtk.get_minor_version() > 18:
            cssProviderFile = Gio.File.new_for_uri(
                'resource:///org/gnome/Eolie/application.css')
        else:
            cssProviderFile = Gio.File.new_for_uri(
                'resource:///org/gnome/Eolie/application-legacy.css')
        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_file(cssProviderFile)
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.settings = Settings.new()
        self.history = DatabaseHistory()
        self.bookmarks = DatabaseBookmarks()
        self.bookmarks.import_firefox()
        self.art = Art()
        self.search = Search()

        shortcut_action = Gio.SimpleAction.new('shortcut',
                                               GLib.VariantType.new('s'))
        shortcut_action.connect('activate', self.__on_shortcut_action)
        self.add_action(shortcut_action)
        self.set_accels_for_action("app.shortcut::uri", ["<Control>l"])
        self.set_accels_for_action("app.shortcut::new_page", ["<Control>t"])
        self.set_accels_for_action("app.shortcut::close_page", ["<Control>w"])

        # Set some WebKit defaults
        context = WebKit2.WebContext.get_default()
        data_manager = WebKit2.WebsiteDataManager()
        context.new_with_website_data_manager(data_manager)
        context.set_process_model(
                            WebKit2.ProcessModel.MULTIPLE_SECONDARY_PROCESSES)
        context.set_cache_model(WebKit2.CacheModel.WEB_BROWSER)
        d = Gio.File.new_for_path(self.__FAVICONS_PATH)
        if not d.query_exists():
            d.make_directory_with_parents()
        context.set_favicon_database_directory(self.__FAVICONS_PATH)
        cookie_manager = context.get_cookie_manager()
        cookie_manager.set_accept_policy(
                                     WebKit2.CookieAcceptPolicy.NO_THIRD_PARTY)
        cookie_manager.set_persistent_storage(
                                        self.__COOKIES_PATH,
                                        WebKit2.CookiePersistentStorage.SQLITE)

    def do_startup(self):
        """
            Init application
        """
        Gtk.Application.do_startup(self)

        if not self.window:
            self.init()
            menu = self.__setup_app_menu()
            if self.prefers_app_menu():
                self.set_app_menu(menu)
                self.window = Window()
            else:
                self.window = Window()
                self.window.setup_menu(menu)
            self.window.show()
            self.window.container.add_web_view("google.fr", True)

    def prepare_to_exit(self, action=None, param=None, exit=True):
        """
            Save window position and view
        """
        if exit:
            self.quit()

    def quit(self):
        """
            Quit Eolie
        """
        self.window.destroy()

#######################
# PRIVATE             #
#######################
    def __settings_dialog(self, action=None, param=None):
        """
            Show settings dialog
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        pass

    def __about(self, action, param):
        """
            Setup about dialog
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/AboutDialog.ui')
        about = builder.get_object('about_dialog')
        about.set_transient_for(self.window)
        about.connect("response", self.__about_response)
        about.show()

    def __shortcuts(self, action, param):
        """
            Show help in yelp
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        try:
            builder = Gtk.Builder()
            builder.add_from_resource('/org/gnome/Eolie/Shortcuts.ui')
            builder.get_object('shortcuts').set_transient_for(self.window)
            builder.get_object('shortcuts').show()
        except:  # GTK < 3.20
            self.__help(action, param)

    def __help(self, action, param):
        """
            Show help in yelp
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        try:
            Gtk.show_uri(None, "help:eolie", Gtk.get_current_event_time())
        except:
            print(_("Eolie: You need to install yelp."))

    def __about_response(self, dialog, response_id):
        """
            Destroy about dialog when closed
            @param dialog as Gtk.Dialog
            @param response id as int
        """
        dialog.destroy()

    def __setup_app_menu(self):
        """
            Setup application menu
            @return menu as Gio.Menu
        """
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/Appmenu.ui')
        menu = builder.get_object('app-menu')

        aboutAction = Gio.SimpleAction.new('about', None)
        aboutAction.connect('activate', self.__about)
        self.add_action(aboutAction)

        shortcutsAction = Gio.SimpleAction.new('shortcuts', None)
        shortcutsAction.connect('activate', self.__shortcuts)
        self.add_action(shortcutsAction)

        helpAction = Gio.SimpleAction.new('help', None)
        helpAction.connect('activate', self.__help)
        self.add_action(helpAction)

        quitAction = Gio.SimpleAction.new('quit', None)
        quitAction.connect('activate', self.prepare_to_exit)
        self.add_action(quitAction)

        return menu

    def __on_activate(self, application):
        """
            Call default handler
            @param application as Gio.Application
        """
        self.window.present()

    def __on_shortcut_action(self, action, param):
        """
            Global shortcuts handler
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        string = param.get_string()
        if string == "uri":
            self.window.toolbar.title.focus_entry()
        elif string == "new_page":
            self.window.container.add_web_view("google.fr", True)
        elif string == "close_page":
            self.window.container.sidebar.current.destroy()
