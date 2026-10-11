import unittest
from unittest import mock

from k3cgrouparch import account


class TestAccount(unittest.TestCase):
    def test_run_sets_value_with_expire_time(self):
        # The value and its expire time are set in one command, so no failure between two commands can leave a
        # value that never expires.
        redis_client = mock.Mock()
        context = {
            "arch_conf": {"value": {}},
            "cgroup_dir": "/sys/fs/cgroup",
            "redis_client": redis_client,
            "redis_prefix": "cgroup_arch",
            "redis_expire_time": 300,
        }

        account._run(context, 1700000000)

        self.assertEqual([mock.call.set("cgroup_arch/account/1700000000", "{}", ex=300)], redis_client.mock_calls)
