import logging
import os

import k3fs

logger = logging.getLogger(__name__)


def create_cgroup(cgroup_path):
    os.mkdir(cgroup_path, 0o755)


def add_pids(cgroup_path, pids):
    task_file = os.path.join(cgroup_path, "tasks")

    for pid in pids:
        try:
            k3fs.fwrite(task_file, str(pid), fsync=False)
        except OSError as e:
            logger.info(f"failed to add pid: {pid} to file: {task_file}, {e!r}")


def clear_pids(subsystem_dir, cgroup_path):
    task_file = os.path.join(cgroup_path, "tasks")
    with open(task_file, "r") as f:
        while True:
            line = f.readline()
            if line == "":
                break

            pid = line.strip()

            add_pids(subsystem_dir, [pid])


def remove_cgroup(subsystem_dir, cgroup_path):
    sub_dirs = k3fs.ls_dirs(cgroup_path)

    for sub_dir in sub_dirs:
        sub_cgroup_path = os.path.join(cgroup_path, sub_dir)
        remove_cgroup(subsystem_dir, sub_cgroup_path)

    clear_pids(subsystem_dir, cgroup_path)
    os.rmdir(cgroup_path)
