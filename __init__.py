"""
#   Name

cgrouparch

A python lib used to build cgroup directory tree, add set cgroup pid.

#   Status

This library is considered production ready.

It supports only cgroup v1.
It manages the `cpu` and `blkio` subsystems in `<cgroup_dir>/<subsystem>`,
such as `/sys/fs/cgroup/cpu`.
It uses v1 files such as `cpu.shares`, `blkio.weight` and `tasks`.
A host that mounts only the cgroup v2 unified hierarchy has none of these files.

#   Description

This lib is used to set up cgroup directory tree according to
configuration saved in zookeeper, and add pid to cgroup accordingly.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

from importlib.metadata import version

__version__ = version("k3cgrouparch")
