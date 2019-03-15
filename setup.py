# -*- coding: utf-8 -*-
# MIT License

# Copyright (c) 2019 Björn Larsson

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages
from ical2org.version import version, name

setup(
    name=name(),
    version=version(),
    url="https://github.com/fuzzycode/ical2org-two",
    project_urls={
        "Documentation": "",
        "Code": "https://github.com/fuzzycode/ical2org-two",
        "Issue tracker": "https://github.com/fuzzycode/ical2org-two/issues",
    },
    license="MIT",
    author="Björn Larsson",
    author_email="develop@bjornlarsson.net",
    maintainer="Björn Larsson",
    maintainer_email="develop@bjornlarsson.net",
    zip_safe=False,
    description="",
    long_description="",
    keywords="ical iCalendar calendar org org-mode emacs",
    platforms=["any"],
    packages=find_packages(),
    install_requires=['icalendar', 'python-dateutil'],
    tests_require=['libfaketime'],
    entry_points={
        'console_scripts': [
            'ical2org2 = ical2org.ical2org:main',
        ],
    },
    python_requires=">=3.4",
    test_suite='tests',
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ]
)
