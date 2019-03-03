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
import re
from string import Template
from dateutil import tz
from icalendar import Calendar as iCal
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from version import version

__description__ = "Converts icalander .ics files to org-agenda format"


def _localized_time(dt):
    """Convert a datetime object to local time"""
    if isinstance(dt, datetime):
        return dt.astimezone(tz.tzlocal())
    else:
        return dt


def _org_time(start, end):
    """"""
    start = _localized_time(start)
    end = _localized_time(end)
    return "{}--{} ".format(start.strftime("%H:%M"), end.strftime("%H:%M"))  # Note the extra padding


def _org_timestamp(dt):
    """Returns a org-mode passive timestamp"""
    t = _localized_time(dt)
    return "[{}]".format(t.strftime("%Y-%m-%d %a %H:%M"))


def _org_range(start, end):
    """"""
    start = _localized_time(start)
    end = _localized_time(end)
    return "(diary-block {start} {end})".format(start=start.strftime("%m %d %Y"),
                                                end=end.strftime("%m %d %Y"))


def _org_date(_date):
    """"""
    return "(diary-date {month} {day} {year})".format(month=_date.month,
                                                      day=_date.day,
                                                      year=_date.year)


def _org_recurrence_range(rule, start):
    if 'UNTIL' in rule:
        end = _localized_time(rule['UNTIL'][0])
        return _org_range(start, end)

    elif 'COUNT' in rule:
        interval = rule.get('INTERVAL', [1])[0]
        count = rule.get('COUNT', [1])[0]
        frequency = rule['FREQ'][0]

        if frequency == 'YEARLY':
            delta = relativedelta(years=(count * interval))
        elif frequency == 'MONTHLY':
            delta = relativedelta(months=count * interval)
        elif frequency == 'WEEKLY':
            delta = relativedelta(weeks=(count * interval) / len(rule['BYDAY']))
        elif frequency == 'DAILY':
            delta = relativedelta(days=(count * interval))
        else:
            delta = timedelta()

        return _org_range(start, start + delta)
    else:
        return ""


def _org_days(rule):
    if not ('BYDAY' in rule or 'BYMONTHDAY' in rule):
        return ""

    if 'BYMONTHDAY' in rule:
        return "(diary-date t '({days}) t)".format(
            days=' '.join(["{}".format(day) for day in rule['BYMONTHDAY']]))
    else:
        day_names = list()
        relative_days = list()
        lookup = {"SU": 0, "MO": 1, "TU": 2, "WE": 3, "TH": 4, "FR": 5, "SA": 6}

        for day in rule['BYDAY']:
            match = re.match(r"(?P<number>\d)(?P<day>[FMSTW][AEHROU])", day)

            if match:
                relative_days.append("(diary-float t {day} {number})".format(day=lookup[match.group('day')],
                                                                             number=match.group('number')))
            else:
                day_names.append(str(lookup[day]))

        days = "(memq (calendar-day-of-week date) '({}))".format(' '.join(day_names)) if len(day_names) > 0 else ""
        return "{} {}".format(' '.join(relative_days), days)


def _org_months(rule):
    if 'BYMONTH' not in rule:
        return ""

    months = ' '.join(rule['BYMONTH'])
    return "(memq (nth 0 date) '({months}))".format(months=months)


def _org_interval(rule, start):
    if 'INTERVAL' not in rule:
        return ""

    interval = rule['INTERVAL'][0]
    frequency = rule['FREQ'][0]
    start = _localized_time(start)

    if frequency == 'DAILY':
        return "(eq 0 (% (- (calendar-absolute-from-gregorian date) \
(calendar-absolute-from-gregorian '({month} {day} {year}))) {interval}))".format(interval=interval,
                                                                       month=start.month,
                                                                       day=start.day,
                                                                       year=start.year)
    elif frequency == 'WEEKLY':
        return "(eq 0 (% (/ (- (calendar-absolute-from-gregorian date) \
(calendar-absolute-from-gregorian '({month} {day} {year}))) 7) {interval}))".format(interval=interval,
                                                                                    month=start.month,
                                                                                    day=start.day,
                                                                                    year=start.year)
    elif frequency == 'MONTHLY':
        return "(eq 0 (% (+ (* (- (nth 2 date) {year}) 12) \
(- (nth 0 date) {month})) {interval}))".format(interval=interval, month=start.month, day=start.day, year=start.year)
    elif frequency == 'YEARLY':
        return "(eq 0 (% (- (nth 2 date) {year}) {interval}))".format(interval=interval,
                                                                      month=start.month,
                                                                      day=start.day,
                                                                      year=start.year)
    else:
        return ""


def _org_exceptions(exceptions):
    if not exceptions:
        return ""

    exceptions = list(exceptions) if not isinstance(exceptions, list) else exceptions
    result = list()
    for e in exceptions:
        result.extend(["(not {date})".format(date=_org_date(d.dt)) for d in e.dts])

    return " ".join(result)


def _yearly_date(dt):
    return "(diary-date {month} {day} t)".format(month=dt.month, day=dt.day)


class Event(object):
    """

    """
    __event_template__ = Template("* ${summary}\n${time}\n\t:PROPERTIES:\n${properties}\n\t:END:\n${description}\n")
    __property_template = Template("\t:${name}: ${value}")
    __recurring_template = Template(
        "%%(and ${date} ${byday} ${range} ${interval} ${bymonth} ${exception}) ${time}${summary}")

    def __init__(self, **kwargs):
        self._data = kwargs

    def is_recurring(self):
        return hasattr(self, 'RRULE')

    def is_all_day(self):
        return type(self._data['DTSTART'].dt) is date

    def _get_properties(self):
        props = [self.__property_template.substitute({'name': "LOCATION",
                                                      "value": self._data['LOCATION']}),
                 self.__property_template.substitute({'name': "ID",
                                                      "value": self._data['UID']}),
                 self.__property_template.substitute({'name': 'CREATED',
                                                      'value': _org_timestamp(self._data['CREATED'].dt)}),
                 self.__property_template.substitute({'name': "LAST-MODIFIED",
                                                      'value': _org_timestamp(self._data['LAST-MODIFIED'].dt)})]
        return "\n".join(props)

    def _get_recurring_time(self):
        frequency = self.RRULE['FREQ'][0]
        _date = _yearly_date(self.DTSTART.dt) if frequency == 'YEARLY' else ""
        _exceptions = getattr(self, 'EXDATE', None)
        return self.__recurring_template.substitute(date=_date,
                                                    summary=self.SUMMARY,
                                                    byday=_org_days(self.RRULE),
                                                    bymonth=_org_months(self.RRULE),
                                                    exception=_org_exceptions(_exceptions),
                                                    range=_org_recurrence_range(self.RRULE, self.DTSTART.dt),
                                                    interval=_org_interval(self.RRULE, self.DTSTART.dt),
                                                    time=_org_time(self.DTSTART.dt, self.DTEND.dt))

    def _get_instance_time(self):
        time = "" if self.is_all_day() else _org_time(self.DTSTART.dt, self.DTEND.dt)
        end = self.DTEND.dt - timedelta(days=1) if self.is_all_day() else self.DTEND.dt
        return "%%(and {range}) {time}{summary}".format(summary=self.SUMMARY,
                                                        time=time,
                                                        range=_org_range(self.DTSTART.dt, end))

    def _get_time(self):
        if self.is_recurring():
            return self._get_recurring_time()
        return self._get_instance_time()

    def _get_description(self):
        desc = self._data.get('DESCRIPTION', None)

        if desc:
            return "** Description:\n\t{}".format(desc.replace('\n', '\n\t'))
        else:
            return ""

    def __str__(self):
        data = dict(properties=self._get_properties(),
                    time=self._get_time(),
                    summary=self._data['SUMMARY'],
                    description=self._get_description())
        return self.__event_template__.substitute(data)

    def __lt__(self, other):
        if self.UID == other.UID:
            return hasattr(self, 'RRULE')
        return self.UID < other.UID

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError("No such attribute: {}".format(item))


class Calendar(object):
    """

    """
    __file_template__ = Template("${header}${body}")
    __header_template__ = Template("# -*- buffer-read-only: t -*-\n${properties}\n\n")
    __header_property_template = Template("#+PROPERTY: ${name} ${value}")

    def __init__(self, stream):
        self._cal = iCal.from_ical(stream.read())
        self._events = sorted([Event(**e) for e in self._cal.walk("VEVENT")])

    def _get_header(self):
        created = _org_timestamp(datetime.now())
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

    settings = vars(parser.parse_args(args[1:]))

    settings['output'].write(str(Calendar(settings['input'])))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
