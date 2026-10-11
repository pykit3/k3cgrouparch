import unittest
from unittest import mock

import k3utfjson
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

    def test_nested_cgroups(self):
        # A cgroup gets one -g argument per subsystem that has it, with its path from the subsystem root. The
        # cgroup tree is not built, so the test changes no real cgroup.
        arch_conf = {
            "cpu": {
                "sub_cgroup": {
                    "test_cgroup_a": {"conf": {"share": 1024}},
                    "test_cgroup_b": {
                        "conf": {"share": 100},
                        "sub_cgroup": {"test_cgroup_b_sub1": {"conf": {"share": 200}}},
                    },
                },
            },
            "blkio": {
                "sub_cgroup": {
                    "test_cgroup_b": {
                        "sub_cgroup": {"test_cgroup_b_sub1": {"conf": {"weight": 100}}},
                    },
                },
            },
        }
        zk_client = mock.Mock(spec=KazooClient)
        zk_client.get.return_value = (k3utfjson.dump(arch_conf), mock.Mock(version=3))

        with (
            mock.patch.object(manager, "get_zk_client", return_value=zk_client),
            mock.patch.object(manager.cgroup_manager, "build_all_subsystem_cgroup_arch") as build,
        ):
            got = manager.get_cgexec_arg(["test_cgroup_a", "test_cgroup_b_sub1", "test_cgroup_c"], **argkv)

        want = {
            "test_cgroup_a": " -g cpu:/test_cgroup_a",
            "test_cgroup_b_sub1": " -g cpu:/test_cgroup_b/test_cgroup_b_sub1 -g blkio:/test_cgroup_b/test_cgroup_b_sub1",
            "test_cgroup_c": "",
        }
        self.assertEqual(want, got)

        zk_client.get.assert_called_once_with("/cluster_a/arch_conf")
        context = build.call_args.args[0]
        self.assertEqual({"version": 3, "value": arch_conf}, context["arch_conf"])


class TestUpdateConf(unittest.TestCase):
    def test_update_conf(self):
        # A changed conf in zookeeper replaces the conf in the context and rebuilds the cgroup tree from it.
        arch_conf = {"cpu": {"sub_cgroup": {"test_cgroup_a": {"conf": {"share": 1024}}}}}
        zk_client = mock.Mock(spec=KazooClient)
        zk_client.get.return_value = (k3utfjson.dump(arch_conf), mock.Mock(version=4))
        context = {"zk_prefix": "/cluster_a", "zk_client": zk_client, "arch_conf": None}

        with (
            mock.patch.dict(manager.global_value, {"context": context}),
            mock.patch.object(manager.cgroup_manager, "build_all_subsystem_cgroup_arch") as build,
        ):
            manager.update_conf(None)

        self.assertEqual({"version": 4, "value": arch_conf}, context["arch_conf"])
        zk_client.get.assert_called_once_with("/cluster_a/arch_conf", watch=manager.update_conf)
        build.assert_called_once_with(context)
