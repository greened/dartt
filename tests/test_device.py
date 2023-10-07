#!/usr/bin/env python3
#
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

import dartt.device as dev
import pytest
from typing import Callable, Dict, Iterable, Sequence

class MockDevice:
    def __init__(
            self,
            Name: str,
            Type: str
    ):
        if Type == 'CD':
            self._Properties = {
                'ID_CDROM_MEDIA': '1',
                'ID_CDROM_MEDIA_CD': '1',
                'ID_CDROM_MEDIA_SESSION_COUNT': '1',
                'ID_CDROM_MEDIA_TRACK_COUNT': '21',
                'ID_CDROM_MEDIA_TRACK_COUNT_AUDIO': '21',
            }
        elif Type == 'DVD':
            self._Properties = {
                'ID_CDROM_MEDIA': '1',
                'ID_CDROM_MEDIA_DVD': '1',
                'ID_CDROM_MEDIA_SESSION_COUNT': '21',
                'ID_CDROM_MEDIA_STATE': 'complete',
                'ID_CDROM_MEDIA_TRACK_COUNT': '1',
                'ID_CDROM_MEDIA_TRACK_COUNT_DATA': '1',
                'ID_FS_APPLICATION_ID': 'DVDAfterEdit',
                'ID_FS_BLOCKSIZE': '2048',
                'ID_FS_LABEL': 'A_GOOD_MOVIE',
                'ID_FS_LABEL_ENC': 'A_GOOD_MOVIE',
                'ID_FS_LOGICAL_VALUE_ID': 'A_GOOD_MOVIE',
                'ID_FS_TYPE': 'udf',
                'ID_FS_USAGE': 'filesystem',
                'ID_FS_UUID': '33fe932d00000000',
                'ID_FS_UUID_ENC': '33fe932d00000000',
                'ID_FS_VERSION': '1.02',
                'ID_FS_VOLUME_ID': 'A_GOOD_MOVIE',
                'ID_FS_VOLUME_SET_ID': '33fe932d',
            }
        elif Type == 'BD':
            self._Properties = {
                'ID_CDROM_MEDIA': '1',
                'ID_CDROM_MEDIA_BD': '1',
                'ID_CDROM_MEDIA_SESSION_COUNT': '21',
                'ID_CDROM_MEDIA_STATE': 'complete',
                'ID_CDROM_MEDIA_TRACK_COUNT': '1',
                'ID_CDROM_MEDIA_TRACK_COUNT_DATA': '1',
                'ID_FS_APPLICATION_ID': 'APPLICATION_ID',
                'ID_FS_BLOCKSIZE': '2048',
                'ID_FS_LABEL': 'Another_Good_Movie',
                'ID_FS_LABEL_ENC': 'Another_Good_Movie',
                'ID_FS_LOGICAL_VALUE_ID': 'Another_Good_Movie',
                'ID_FS_TYPE': 'udf',
                'ID_FS_USAGE': 'filesystem',
                'ID_FS_UUID': '33fe932d91fa3de2',
                'ID_FS_UUID_ENC': '33fe932d91fa3de2',
                'ID_FS_VERSION': '2.50',
                'ID_FS_VOLUME_ID': 'Another_Good_Movie',
                'ID_FS_VOLUME_SET_ID': '33FE932D91fA3DE2_VOLUME_SET_ID',
            }
        else:
            self._Properties = {}

        self._Properties['ID_CDROM'] = '1'
        self._SysName = Name

    @property
    def properties(
            self
    ) -> Dict[str, str]:
        return self._Properties

    def keys(
            self
    ) -> Iterable[str]:
        return self._Properties.keys()

    @property
    def sys_name(
            self
    ) -> str:
        return self._SysName

class MockDevices:
    def __init__(
            self,
            Names: Sequence[str],
            Type: str
    ):
        self._Names = Names
        self._Type = Type

    def match(self, **kwargs):
        return [ MockDevice(Name, self._Type) for Name in self._Names ]

@pytest.fixture
def deviceFactory(
        request
) -> Callable[[Sequence[str]], MockDevice]:
    def makeDevices(
            Names: Sequence[str],
            DiscType: str
    ) -> MockDevices:
        return MockDevices(Names, DiscType)

    return makeDevices

@pytest.mark.parametrize(
    'DeviceNames', [ 'sr0', 'sr1', [ 'sr0', 'sr3' ] ]
)
def test_detectOpticalDrives(
        monkeypatch,
        deviceFactory,
        DeviceNames
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: deviceFactory(DeviceNames, 'CD')
    )

    assert dev.detectOpticalDrives()

    for Device, Name in zip(dev.detectOpticalDrives(), DeviceNames):
        assert Device.id == Name

@pytest.mark.parametrize(
    'DiscType,ExpectedType', [
        ('CD', dev.AudioCD), ('DVD', dev.DVD), ('BD', dev.BluRay)
    ]
)

def test_Device_open(
        monkeypatch,
        deviceFactory,
        DiscType,
        ExpectedType
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: deviceFactory(['sr0'], DiscType)
    )

    assert dev.detectOpticalDrives()

    for Device in dev.detectOpticalDrives():
        assert isinstance(Device.open(), ExpectedType)

def test_Device_open_failure(
        monkeypatch,
        deviceFactory
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: deviceFactory(['sr0', 'sr6'], '')
    )

    assert dev.detectOpticalDrives()

    for Device in dev.detectOpticalDrives():
        with pytest.raises(RuntimeError):
            Disc = Device.open()
