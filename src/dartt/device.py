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

from abc import ABC, abstractmethod
import logging
from pathlib import Path
import pyudev
import sh
from typing import Iterable

import dartt.config as config

class DeviceNotReadyError(RuntimeError):
    def __init__(self, DevPath: str):
        super().__init__(
            f'{DevPath} not ready or does not contain a known disc type'
        )

class Device(ABC):
    @property
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def open(self):
        pass
