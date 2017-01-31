# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# Copyright (c) 2015 Jean-Philippe Braun <eon@patapon.info>
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

from threading import current_thread

from eolie.define import El


class SqlCursor:
    """
        Context manager to get the SQL cursor
    """
    def add(obj):
        """
            Add cursor to thread list
            Raise an exception if cursor already exists
        """
        name = current_thread().getName() + obj.__class__.__name__
        El().cursors[name] = obj.get_cursor()

    def __init__(self, obj):
        """
            Init object
        """
        self._obj = obj
        self._creator = False

    def __enter__(self):
        """
            Return cursor for thread, create a new one if needed
        """
        name = current_thread().getName() + self._obj.__class__.__name__
        if name not in El().cursors:
            self._creator = True
            El().cursors[name] = self._obj.get_cursor()
        return El().cursors[name]

    def __exit__(self, type, value, traceback):
        """
            If creator, close cursor and remove it
        """
        if self._creator:
            name = current_thread().getName() + self._obj.__class__.__name__
            El().cursors[name].close()
            del El().cursors[name]
