import unittest
from unittest import mock

from kazoo.client import KazooClient
from kazoo.exceptions import ConnectionLoss

from k3cgrouparch import manager

argkv = {
    "get_zk_host": lambda: "127.0.0.1:2181",
    "zk_prefix": "/cluster_a",
    "zk_auth_data": [("digest", "super:123456")],
}


class TestGetCgexecArg(unittest.TestCase):
    def test_zk_error(self):
        # A failed lookup must not look like a configuration without cgroup limits, and must not leak the client.
        err = ConnectionLoss()
        zk_client = mock.Mock(spec=KazooClient)
        zk_client.get.side_effect = err

        with (
            mock.patch.object(manager, "get_zk_client", return_value=zk_client),
            self.assertRaises(ConnectionLoss) as ctx,
        ):
            manager.get_cgexec_arg(["test_cgroup_a"], **argkv)

        self.assertIs(err, ctx.exception)
        zk_client.stop.assert_called_once_with()
        zk_client.close.assert_called_once_with()
