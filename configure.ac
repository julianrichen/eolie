AC_PREREQ(2.63)
AC_INIT([eolie],
        [0.1.0],
        [https://github.com/gnumdk/eolie],
        [eolie],
        [https://github.com/gnumdk/eolie])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS(config.h)
AM_INIT_AUTOMAKE([1.11 tar-ustar dist-xz no-dist-gzip -Wno-portability subdir-objects])
AM_MAINTAINER_MODE([enable])
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])

AM_PATH_PYTHON(3.0)
AM_PYTHON_CHECK_VERSION(3.0)

GETTEXT_PACKAGE=eolie
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE",
                   [The prefix for our gettext translation domains.])
IT_PROG_INTLTOOL(0.26)

PKG_PROG_PKG_CONFIG([0.22])

GLIB_GSETTINGS
YELP_HELP_INIT
GOBJECT_INTROSPECTION_REQUIRE([1.35.9])
PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= 3.14])

GLIB_COMPILE_RESOURCES=`$PKG_CONFIG --variable glib_compile_resources gio-2.0`
WEB_EXT_FLAGS=`$PKG_CONFIG pygobject-3.0 webkit2gtk-web-extension-4.0 python3 --cflags`
WEB_EXT_LIBS=`$PKG_CONFIG pygobject-3.0 webkit2gtk-web-extension-4.0 python3 --libs`
AC_SUBST(GLIB_COMPILE_RESOURCES)

AC_CONFIG_FILES([
  Makefile
  data/Makefile
  data/AboutDialog.ui
  src/Makefile
  po/Makefile.in
])
AC_OUTPUT
