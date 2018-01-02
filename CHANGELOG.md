# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Under [Semantic Versioning](http://semver.org/spec/v2.0.0.html), vX.Y.Z ,
- Z will be bumped if there's a patch or bugfix.
- Y will be bumped with new features (commands)
- X will be bumped if the code released is no longer backwards compatible with previous versions.

## [Unreleased]

## [Released]
### [1.3.5] - 2018-02-02
### Changed
- Fixed exception when faced with multiple term timetables
- Some users have multi-term timetables, alternating between term 1 and term 2.
- Not really sure why this is done but it has to be addressed given that there's no proper API to rip the TT
- Modified selenium to do a couple of clicks if detected.
- The bot will always select the latest timetable to display if given a choice.
- Commited in [#9ce5126](https://github.com/xlanor/SIM-UoW-Timetable-bot/commit/9ce51262927ad6999e1e049585605e23d8eb4541)
- Fixed issue with inline buttons
- Timetables may have a gap in between with 1(or more) weeks where there are no classes.
- Previous behaviour by the bot was to check if there are classes next week, if there are no classes, it will not give an option to navigate further
- Rewrote behaviour to search if there are classes in the doccument that have a date value gt/lt than current date.
- If there are classes, it will display the button, allowing users to navigate through the date with no classes.
- Commited in [#87276d0](https://github.com/xlanor/SIM-UoW-Timetable-bot/commit/87276d02cfa14c734f3677b05a1553177a246b55)

### [1.3.4] - 2017-10-25
### Changed
- Added a check to prevent the bot from throwing an exception when users who cancelled halfway through the timetable are scanned during the alerts

### [1.3.3] - 2017-10-24
### Changed
- Fixed a bug with new users and nightly alerts

### [1.3.2] - 2017-10-23
### Changed
- Fixed wrong variable name being used

### [1.3.1] - 2017-10-21
### Changed
- Tweaked formatting

### [1.3.0] - 2017-10-20
### Added
- Nightly alerting system at 2130 for the next day's schedule

### Changed
- Fixed daytime alert formatting.

### [1.2.0] - 2017-10-17
### Added
- Added alerting system to remind users at 0730H each morning

### Changed
- Fixed some minor bugs.

### [1.1.0] - 2017-10-11
### Added
- Added scrolling feature to timetable **beta**

### Changed
- Fixed validation
- Restricted key length to 16 and below.

## [1.0.0] - 2017-10-10
### Added
- Initial release
- Returns timetable for the week

### Changed
