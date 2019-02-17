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

"""

"""

import sys
import argparse
from icalendar import Calendar as iCal
from .version import version

__description__ = "Converts icalander .ics files to org-agenda format"
__config__ = None


def main(args):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(version()))
    parser.add_argument('--input', type=argparse.FileType(mode='r', encoding='utf8'), default=sys.stdin)
    parser.add_argument('--output', type=argparse.FileType(mode='w', encoding='utf8'), default=sys.stdout)
    global __config__
    __config__ = vars(parser.parse_args(args[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
