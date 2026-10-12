# k3cgrouparch

[![Action-CI](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3cgrouparch/badge/?version=stable)](https://k3cgrouparch.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3cgrouparch)](https://pypi.org/project/k3cgrouparch)

Set up cgroup directory tree according to configuration saved in zookeeper, and add pid to cgroup accordingly.

k3cgrouparch is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3cgrouparch
```

## Quick Start

`manager.run()` reads the cgroup tree from the ZooKeeper node `<zk_prefix>/arch_conf` and builds it under `cgroup_dir`. Then it keeps adding the pids in each cgroup's pid files to that cgroup, and never returns.

```python
from k3cgrouparch import manager


def get_cgroup_pid_file(cgroup_name):
    if cgroup_name == "test_cgroup_a":
        return ["/tmp/test.pid"]
    # ...


def get_zk_host():
    return "127.0.0.1:2181,1.2.3.4:2181"


argkv = {
    "cgroup_dir": "/sys/fs/cgroup",
    "get_cgroup_pid_file": get_cgroup_pid_file,
    "get_zk_host": get_zk_host,
    "zk_prefix": "/cluster_a/service_rank",
    "zk_auth_data": [("digest", "super:123456")],
    "communicate_ip": "127.0.0.1",
    "communicate_port": 3344,
    "redis_ip": "127.0.0.1",
    "redis_port": 6379,
}

manager.run(**argkv)
```

`manager.get_cgexec_arg()` builds the same tree and returns the `cgexec` arguments of each cgroup. This example reads the tree `{"cpu": {"sub_cgroup": {"test_cgroup_a": {"conf": {"share": 1024}}}}}`:

```python
argkv = {
    "cgroup_dir": "/sys/fs/cgroup",
    "get_zk_host": get_zk_host,
    "zk_prefix": "/cluster_a/service_rank",
    "zk_auth_data": [("digest", "super:123456")],
}
cgexec_arg = manager.get_cgexec_arg(["test_cgroup_a"], **argkv)
# {"test_cgroup_a": " -g cpu:/test_cgroup_a"}
```

## API Reference

::: k3cgrouparch

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
