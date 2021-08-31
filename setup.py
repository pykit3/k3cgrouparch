# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3cgrouparch",
    packages=["k3cgrouparch"],
    version="0.1.0",
    license='MIT',
    description='This lib is used to set up cgroup directory tree according to configuration saved in zookeeper, and add pid to cgroup accordingly.',
    long_description="# k3cgrouparch\n\n[![Action-CI](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3cgrouparch.svg?branch=master)](https://travis-ci.com/pykit3/k3cgrouparch)\n[![Documentation Status](https://readthedocs.org/projects/k3cgrouparch/badge/?version=stable)](https://k3cgrouparch.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3cgrouparch)](https://pypi.org/project/k3cgrouparch)\n\nThis lib is used to set up cgroup directory tree according to configuration saved in zookeeper, and add pid to cgroup accordingly.\n\nk3cgrouparch is a component of [pykit3] project: a python3 toolkit set.\n\n\n#   Name\n\ncgrouparch\n\nA python lib used to build cgroup directory tree, add set cgroup pid.\n\n#   Status\n\nThis library is considered production ready.\n\n#   Description\n\nThis lib is used to set up cgroup directory tree according to\nconfiguration saved in zookeeper, and add pid to cgroup accordingly.\n\n\n\n\n# Install\n\n```\npip install k3cgrouparch\n```\n\n# Synopsis\n\n```python\n\n# {\n#     'cpu': {\n#         'sub_cgroup': {\n#             'test_cgroup_a': {\n#                 'conf': {\n#                     'share': 1024,\n#                 },\n#             },\n#             'test_cgroup_b': {\n#                 'conf': {\n#                     'share': 100,\n#                 },\n#                 'sub_cgroup': {\n#                     'test_cgroup_b_sub1': {\n#                         'conf': {\n#                             'share': 200,\n#                         },\n#                     },\n#                 },\n#             },\n#         },\n#     },\n# }\n\nfrom k3cgrouparch import manager\n\n\ndef get_cgroup_pid_file(cgroup_name):\n    if cgroup_name == 'test_cgroup_a':\n        return ['/tmp/test.pid']\n    # ...\n\n\ndef get_zk_host():\n    return '127.0.0.1:2181,1.2.3.4:2181'\n\n\nargkv = {\n    'cgroup_dir': '/sys/fs/cgroup',\n    'get_cgroup_pid_file': get_cgroup_pid_file,\n    'get_zk_host': get_zk_host,\n    'zk_prefix': '/cluser_a/service_rank',\n    'zk_auth_data': [('digest', 'super:123456')],\n    'communicate_ip': '127.0.0.1',\n    'communicate_port': '3344',\n}\n\nmanager.run(**argkv)\n\nargkv = {\n    'cgroup_dir': '/sys/fs/cgroup',\n    'get_zk_host': get_zk_host,\n    'zk_prefix': '/cluser_a/service_rank',\n    'zk_auth_data': [('digest', 'super:123456')],\n}\ncgexec_arg = manager.get_cgexec_arg(['test_cgroup_a'], **argkv)\n\n# return like:\n# {\n#     'test_cgroup_a': '-g cpu:test_cgroup_a',\n# }\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3",
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3cgrouparch',
    keywords=['python', 'zookeeper'],
    python_requires='>=3.0',

    install_requires=['k3ut<0.2,>=0.1.15', 'k3fs>=0.1.0,<=0.2.0', 'k3utfjson<0.2,>=0.1.1', 'k3thread>=0.1.0,<0.2', 'psutil>=5.8.0', 'redis>=3.5.0', 'kazoo>=2.8.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
