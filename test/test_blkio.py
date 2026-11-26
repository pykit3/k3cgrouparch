import mmap
import multiprocessing
import os
import random
import sys
import tempfile
import time
import unittest

import k3fs
import k3ut

from k3cgrouparch import blkio, cgroup_manager, cgroup_util

dd = k3ut.dd

random.seed(time.time())

base_dir = os.path.dirname(__file__)


def _cgroup_test_skip_reason() -> str | None:
    """Return why the blkio cgroup test cannot run on this host, or None if it can."""
    if sys.platform != "linux":
        return "cgroup tests run only on Linux"
    if k3ut.has_env("TRAVIS=true") or k3ut.has_env("CI=true"):
        return "cgroup tests do not run in CI"
    # k3cgrouparch supports only cgroup v1; a host that mounts only cgroup v2 has no blkio directory.
    if not os.path.isdir("/sys/fs/cgroup/blkio"):
        return "requires the cgroup v1 blkio hierarchy at /sys/fs/cgroup/blkio"
    return None


def _blkio_worker(index, duration, result_dict):
    # Module-level so that multiprocessing can pickle it: the forkserver and
    # spawn start methods pickle the target, and a bound method would drag in
    # the TestCase that pytest attaches unpicklable fixtures to.

    # wait for the cgroup directory tree to be setup.
    time.sleep(0.2)

    m = mmap.mmap(-1, 1024 * 1024 * 2)
    data = " " * 1024 * 1024 * 2
    m.write(data.encode())

    file_path = os.path.join(base_dir, f"test_file_{index}")
    f = os.open(file_path, os.O_CREAT | os.O_DIRECT | os.O_TRUNC | os.O_RDWR)

    start_time = time.time()
    dd(f"worker {index} {os.getpid()} started at: {start_time:f}")

    count = 0
    while True:
        os.write(f, m)
        count += 1
        dd(f"worker {index} {os.getpid()} wrote {count} times")

        if time.time() - start_time > duration:
            break

    dd(f"worker {index} {os.getpid()} stoped at: {time.time():f}")

    result_dict[index] = count

    os.close(f)


class TestBlkio(unittest.TestCase):
    def test_account(self):
        cgroup_path = tempfile.mkdtemp()
        k3fs.fwrite(
            cgroup_path,
            "blkio.io_service_bytes_recursive",
            "8:0 Read 1053712384\n"
            "8:0 Write 81929383424\n"
            "8:0 Sync 80865775616\n"
            "8:0 Async 2117320192\n"
            "8:0 Total 82983095808\n"
            "8:16 Read 1024\n"
            "8:16 Write 2048\n"
            "Total 82983098880\n",
        )

        got = blkio.account(cgroup_path)

        want = {
            "8:0": {"Read": 1053712384, "Write": 81929383424},
            "8:16": {"Read": 1024, "Write": 2048},
        }
        self.assertEqual(want, got)

        k3fs.remove(cgroup_path)

    def test_blkio_weight(self):
        skip_reason = _cgroup_test_skip_reason()
        if skip_reason is not None:
            self.skipTest(skip_reason)

        manager = multiprocessing.Manager()
        result_dict = manager.dict()

        p1 = multiprocessing.Process(target=_blkio_worker, args=(1, 10, result_dict))
        p1.daemon = True
        p1.start()

        p2 = multiprocessing.Process(target=_blkio_worker, args=(2, 10, result_dict))
        p2.daemon = True
        p2.start()

        p3 = multiprocessing.Process(target=_blkio_worker, args=(3, 10, result_dict))
        p3.daemon = True
        p3.start()

        p4 = multiprocessing.Process(target=_blkio_worker, args=(4, 10, result_dict))
        p4.daemon = True
        p4.start()

        arch_conf = {
            "blkio": {
                "sub_cgroup": {
                    "test_cgroup_a": {
                        "conf": {
                            "weight": int(500 * 0.95),
                        },
                        "sub_cgroup": {
                            "test_cgroup_a_sub1": {
                                "conf": {
                                    "weight": 500,
                                    "pids": [p1.pid],
                                },
                            },
                            "test_cgroup_a_sub2": {
                                "conf": {
                                    "weight": 500,
                                    "pids": [p2.pid],
                                },
                            },
                        },
                    },
                    "test_cgroup_b": {
                        "conf": {
                            "weight": int(500 * 0.05),
                        },
                        "sub_cgroup": {
                            "test_cgroup_b_sub1": {
                                "conf": {
                                    "weight": 500,
                                    "pids": [p3.pid],
                                },
                            },
                            "test_cgroup_b_sub2": {
                                "conf": {
                                    "weight": 500,
                                    "pids": [p4.pid],
                                },
                            },
                        },
                    },
                },
            },
        }

        context = {
            "cgroup_dir": "/sys/fs/cgroup",
            "arch_conf": {"value": arch_conf},
        }

        cgroup_manager.build_all_subsystem_cgroup_arch(context)
        cgroup_manager.set_cgroup(context)

        p1.join()
        p2.join()
        p3.join()
        p4.join()

        for cgrou_name in arch_conf["blkio"]["sub_cgroup"]:
            cgroup_util.remove_cgroup(
                os.path.join(context["cgroup_dir"], "blkio"), os.path.join(context["cgroup_dir"], "blkio", cgrou_name)
            )

        for i in range(1, 5):
            k3fs.remove(os.path.join(base_dir, f"test_file_{i}"))

        dd(result_dict)

        self.assertGreater(result_dict[1] + result_dict[2], result_dict[3] + result_dict[4])
