ACLOCAL_AMFLAGS = -I m4
NULL =

bin_SCRIPTS = eolie

SUBDIRS = src data python-webextension

EXTRA_DIST = \
	eolie.in\
	python-webextension/extension.py.in\
	$(NULL)

webkitextensiondir = $(datadir)/eolie/webkitextension
webkitextension_DATA = python-webextension/pythonloader.so python-webextension/extension.py


CLEANFILES = \
	$(bin_SCRIPTS)\
	$(NULL)

MAINTAINERCLEANFILES = \
	$(srcdir)/AUTHORS \
	$(srcdir)/INSTALL \
	$(srcdir)/aclocal.m4 \
	$(srcdir)/autoscan.log \
	$(srcdir)/compile \
	$(srcdir)/config.guess \
	$(srcdir)/config.h.in \
	$(srcdir)/config.sub \
	$(srcdir)/configure.scan \
	$(srcdir)/depcomp \
	$(srcdir)/install-sh \
	$(srcdir)/ltmain.sh \
	$(srcdir)/missing \
	$(srcdir)/mkinstalldirs \
	$(NULL)

GITIGNOREFILES = \
	m4 \
	$(NULL)

python-webextension/extension.py: python-webextension/extension.py.in Makefile
	$(AM_V_GEN)sed                                          \
		-e s!\@pythondir\@!$(pythondir)!        \
		-e s!\@pyexecdir\@!$(pyexecdir)!        \
		< $< > $@
	chmod a+x $@

eolie: eolie.in Makefile
	$(AM_V_GEN)sed						\
		-e s!\@srcdir\@!$(abs_top_srcdir)!	\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@pkglibdir\@!$(pkglibdir)!	\
		-e s!\@localedir\@!$(localedir)!	\
		-e s!\@pythondir\@!$(pythondir)!	\
		-e s!\@pyexecdir\@!$(pyexecdir)!	\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		< $< > $@
	chmod a+x $@

all-local: eolie

-include $(top_srcdir)/git.mk

