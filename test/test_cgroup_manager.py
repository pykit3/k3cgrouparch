import os
import subprocess
import tempfile
import unittest

import k3fs

from k3cgrouparch import cgroup_manager


class TestCgroupManager(unittest.TestCase):
    def test_get_cgroup_pids(self):
        # A pid file adds its process and the children of it. A malformed or missing pid file adds no pid.
        proc = subprocess.Popen(["sleep", "60"])
        self.addCleanup(proc.wait)
        self.addCleanup(proc.kill)

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        pid_file = os.path.join(tmp.name, "a.pid")
        k3fs.fwrite(pid_file, f"{proc.pid}\n")
        malformed_pid_file = os.path.join(tmp.name, "b.pid")
        k3fs.fwrite(malformed_pid_file, "abc")
        missing_pid_file = os.path.join(tmp.name, "c.pid")

        got = cgroup_manager.get_cgroup_pids([pid_file, malformed_pid_file, missing_pid_file])

        self.assertEqual([proc.pid], got)
