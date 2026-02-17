# Changelog

All notable changes to this package will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-10-18

### Bugfix

- Fixed a bug where package compilation would fail if Vivox is used alongside Moderation

## [1.0.0] - 2024-10-02

### Added

- Documentation for all public APIs of the Moderation SDK

### Removed

- Experimental player custom properties feature

## [1.0.0-pre.3] - 2024-03-18

### Added

- Added Apple Privacy Manifest

### Bugfix

- Fixed a bug where Package initialization would crash if Vivox was part of the project dependencies.

## [1.0.0-pre.2] - 2023-11-09

### Bugfix

- Lowered minimum Vivox-Unity dependency to 16.0.0-pre.1 for automatic Vivox information collection.

## [1.0.0-pre.1] - 2023-09-19

### Report Creation revamped

- Report is now created through the Moderation instance.
- Report now contains the vivox information (and channels) that will be sent to the service, allowing for the game developer to alter it.

## [0.1.0-preview.4] - 2023-09-19

### Bugfix

- Fixed a bug with PlayerCache when a player was leaving / joining the same channel.

## [0.1.0-preview.3] - 2023-07-13

### API Revamp

- Reports now only needs a player id
- Vivox infos are cached and automatically retrieved

## [0.1.0-preview.2] - 2023-03-20

### Prepare for Release

- Improve error management
- Update license.md
- Remove useless editor files

## [0.1.0-preview.1] - 2022-11-15

### This is the first release of the *Moderation* SDK.

- Working prototype of the Moderation SDK package.
