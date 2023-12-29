# SPDX-FileCopyrightText: 2023-present David A. Greene <dag@obbligato.org>

# SPDX-License-Identifier: AGPL-3.0-or-later

# Copyright 2023 David A. Greene

# This file is part of dartt

# dartt is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along
# with dartt. If not, see <https://www.gnu.org/licenses/>.

import argparse
from collections.abc import Iterable
from enum import Enum
import logging
from pathlib import Path
import sys

def parseArgs(
        Args: Iterable
) -> argparse.Namespace:
    Parser = argparse.ArgumentParser(
        prog='dartt',
        description='Disc Archive, Rip, Transcode and Tag'
    )

    Parser.add_argument(
        '--msg-level',
        choices=['debug', 'info', 'warning', 'error'],
        default='error'
    )

    return Parser.parse_args(Args)

def main():
    class ExitCode(Enum):
        DeviceNotReady = 1

    ParsedArgs = parseArgs(sys.argv[1:])

    LogLevel = ParsedArgs.msg_level
    NumericLogLevel = getattr(logging, LogLevel.upper())

    logging.basicConfig(level=NumericLogLevel)

    from dartt.config import readConfig
    Config = readConfig()

    from dartt.device import detectOpticalDrives
    OpticalDrives = detectOpticalDrives(Config)

    from dartt.device import DeviceNotReadyError
    for Drive in OpticalDrives:
        try:
            Media = Drive.open()
        except DeviceNotReadyError as RE:
            print(str(RE))
            return ExitCode.DeviceNotReady.value
