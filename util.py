import logging

import k3fs
import psutil

logger = logging.getLogger(__name__)


def get_pid_from_file(pid_file):
    data = k3fs.fread(pid_file)
    return int(data)


def get_all_pids(pid):
    all_pids = []

    try:
        process = psutil.Process(pid)

    except psutil.NoSuchProcess:
        logger.info(f"process {pid:d} does not exist")
        return all_pids

    except Exception:
        logger.exception(f"faild to get process of pid: {pid:d}")
        return all_pids

    all_pids.append(process.pid)

    children = process.children(recursive=True)
    for process in children:
        all_pids.append(process.pid)

    return all_pids
