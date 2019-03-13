.. image:: https://travis-ci.com/fuzzycode/ical2org-two.svg?branch=master
    :target: https://travis-ci.com/fuzzycode/ical2org-two

.. image:: https://img.shields.io/github/license/fuzzycode/ical2org-two.svg
    :target: https://opensource.org/licenses/MIT

About
=====
Converts ical data into Emacs org-mode entries, suitable for usage in agenda mode.

Install
=======

Usage
=====

Design Goals
============
All events from iCalendar are mapped to org Sexp diary entries. This provides a 1-1 mapping between iCalendar
entries and entries in org mode. It also assures that infinite recurring events can be supported without
risk of bloating resulting file size. It also allows for creating more complex recurrence rules, matching more
closely the once in iCalendar.

ical2org-two does not support the full RFC 2445 iCalandar specification and will
most likely never do so. The goals for this project are, in order of importance:

- Support all dates configurable through Google Calendar
- Support all dates configurable through Office 365
- Support custom tagging through cli configuration
- Support extracting custom properties through cli configuration
- Support filtering through cli configuration
- Support full iCalendar specifications

Known Issues
============
The following items from iCalendar are not yet supported.

- BYSECOND, BYMINUTE and BYHOUR recurring events are not supported
- Exception rules are not supported


Contribute
==========
All contributions are much appreciated.

Code
----

Issues
------

Alternatives
============

License
=======
MIT License, Copyright (c) 2019 Björn Larsson. See LICENSE file for details.