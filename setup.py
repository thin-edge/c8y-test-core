# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["c8y_test_core"]

package_data = {"": ["*"]}

install_requires = [
    "c8y-api>=1.3,<2.0",
    "jwt>=1.3.1,<2.0.0",
    "requests-toolbelt>=0.9.1,<0.10.0",
    "requests>=2.26.0,<3.0.0",
    "tenacity>=8.0.1,<9.0.0",
]

setup_kwargs = {
    "name": "c8y_test_core",
    "version": "0.0.1",
    "description": "pytest plugin for Cumulocity IoT",
    "long_description": "c8y_test_core\n===============\n\nc8y_test_core is an testing library which can be used used to build plugs for testing frameworks such as pytest and Robot Framework. It provides easy to use assertions and command to\nsupport `Cumulocity IoT <https://www.softwareag.cloud/site/product/cumulocity-iot.html>`_ based tests.\n\nResources\n---------\n\n- `Issue Tracker <http://github.com/reubenmiller/c8y_test_core/issues>`_\n- `Code <http://github.com/reubenmiller/c8y_test_core/>`_\n",
    "author": "Reuben Miller",
    "author_email": "reuben.d.miller@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/reubenmiller/c8y_test_core",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.7.2,<4.0.0",
}

setup(**setup_kwargs)
