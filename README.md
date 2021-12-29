# Restic Automator
Simple python script to watch directories and trigger restic backup when watching folder has been modified.

## Configuration
Refer to `config.yml`

This script can be daemonized in combination with systemd on linux or launchd on macOS.

## [Restic](https://github.com/restic/restic)
Restic is a fast backup program with strong encryption and wide range of storage backend support.

### Dependencies
- [watchdog](https://github.com/gorakhargosh/watchdog)