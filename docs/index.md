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

```python
from k3cgrouparch import manager

# Initialize cgroup manager with zookeeper config
mgr = manager.Manager(zk_hosts='127.0.0.1:2181')
```

## API Reference

::: k3cgrouparch

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
