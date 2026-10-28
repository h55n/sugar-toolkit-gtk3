#!/usr/bin/env python3

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest
from unittest import mock

try:
    from gi.repository import TelepathyGLib
    from sugar3.presence import connectionmanager
except ImportError:
    # needs the TelepathyGLib typelib (gir1.2-telepathyglib-0.12)
    connectionmanager = None

ACCOUNT = '/org/freedesktop/Telepathy/Account/salut/local_xmpp/account0'


@unittest.skipIf(connectionmanager is None, 'TelepathyGLib is not available')
class ConnectionManagerTest(unittest.TestCase):

    def _manager(self):
        # skip __init__, it needs a running Telepathy account manager
        manager = connectionmanager.ConnectionManager.__new__(
            connectionmanager.ConnectionManager)
        manager._connections_per_account = {}
        return manager

    def test_status_changed_updates_tracked_connection(self):
        manager = self._manager()
        conn = connectionmanager.Connection(ACCOUNT, mock.Mock())
        manager._connections_per_account[ACCOUNT] = conn

        manager._ConnectionManager__status_changed_cb(
            ACCOUNT, TelepathyGLib.ConnectionStatus.CONNECTED, 0)
        self.assertTrue(conn.connected)

        manager._ConnectionManager__status_changed_cb(
            ACCOUNT, TelepathyGLib.ConnectionStatus.DISCONNECTED, 0)
        self.assertFalse(conn.connected)

    def test_status_changed_for_untracked_account_is_ignored(self):
        # a StatusChanged signal can arrive after the account's
        # connection was dropped from the tracked connections
        manager = self._manager()

        manager._ConnectionManager__status_changed_cb(
            ACCOUNT, TelepathyGLib.ConnectionStatus.CONNECTED, 0)

        self.assertEqual(manager._connections_per_account, {})


if __name__ == '__main__':
    unittest.main()
