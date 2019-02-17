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
from string import Template
from icalendar import Calendar as iCal
from datetime import datetime, date, timedelta
from version import version

__description__ = "Converts icalander .ics files to org-agenda format"
__config__ = None


class Event(object):
    """

    """
    __event_template__ = Template("* ${summary}\n${time}\n\t:PROPERTIES:\n${properties}\n\t:END:\n\t${description}\n")
    __property_template = Template("\t${name}: ${value}")

    def __init__(self, **kwargs):
        self._data = kwargs

    def _get_properties(self):
        props = [ self.__property_template.substitute({'name': "LOCATION",
                                                       "value": self._data['LOCATION']})

        ]
        return "\n".join(props)

    def _get_time(self):
        return ""

    def __str__(self):
        data = dict(properties=self._get_properties(),
                    time=self._get_time(),
                    summary=self._data['SUMMARY'],
                    description=self._data['DESCRIPTION'].replace('\n', '\n\t'))
        return self.__event_template__.substitute(data)

    def __lt__(self, other):
        if self.UID == other.UID:
            return hasattr(self, 'RRULE')
        return self.UID < other.UID

    def __getattr__(self, item):
        return self._data[item]


class Calendar(object):
    """

    """
    __file_template__ = Template("${header}${body}")
    __header_template__ = Template("# -*- buffer-read-only: t -*-\n${properties}\n")
    __header_property_template = Template("#+${name}: ${value}")

    def __init__(self, stream):
        self._cal = iCal.from_ical(stream.read())
        self._events = sorted([Event(**e) for e in self._cal.walk("VEVENT")])

    def _get_header(self):
        created = "[{}]".format(datetime.now().strftime("%Y-%m-%d %a %H:%M"))
        props = [self.__header_property_template.substitute(dict(name='PRODID', value=self._cal['PRODID'])),
                 self.__header_property_template.substitute(dict(name="VERSION", value=self._cal['VERSION'])),
                 self.__header_property_template.substitute(dict(name="CREATED", value=created))]

        return self.__header_template__.substitute(dict(properties="\n".join(props)))

    def _get_events(self):
        return "\n".join([str(e) for e in self._events])

    def __str__(self):
        return self.__file_template__.substitute(dict(header=self._get_header(), body=self._get_events()))

    def __repr__(self):
        return "Calendar ({} Events)".format(len(self._events))


def main(args):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(version()))
    parser.add_argument('--input', type=argparse.FileType(mode='r', encoding='utf8'), default=sys.stdin)
    parser.add_argument('--output', type=argparse.FileType(mode='w', encoding='utf8'), default=sys.stdout)
    global __config__
    __config__ = vars(parser.parse_args(args[1:]))

    __config__['output'].write(str(Calendar(__config__['input'])))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
