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

from dartt.config import readConfig
from dartt.disc import AudioCD, Disc, DVD, BluRay

class Device(ABC):
    @property
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def open(self):
        pass

class OpticalDrive(Device):
    def __init__(self, Device: pyudev.Device):
        self._Device = Device

    def __repr__(self) -> str:
        return f'{self._Device.sys_name}'

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def id(self) -> str:
        return self._Device.sys_name

    def open(self) -> Disc:
        if 'ID_CDROM_MEDIA_CD' in self._Device.keys():
            return AudioCD(self)
        if 'ID_CDROM_MEDIA_DVD' in self._Device.keys():
            return DVD(self)
        if 'ID_CDROM_MEDIA_BD' in self._Device.keys():
            return BluRay(self)

        raise RuntimeError(
            '{self.id} not ready or  does not contain a known disc type'
        )

def detectOpticalDrives() -> Iterable[OpticalDrive]:
    Context = pyudev.Context()
    Devices = Context.list_devices(subsystem='block', DEVTYPE='disk')

    return [OpticalDrive(Device) for Device in Devices.match(ID_CDROM=1)
            if 'ID_CDROM' in Device.keys()]
