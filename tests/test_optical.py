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

import dartt.optical as optical
from dartt.audiocd import AudioCD
from dartt.dvd import DVD
from dartt.bluray import BluRay
import discid
import pytest
import sh
from typing import Callable, Dict, Iterable, Sequence

@pytest.mark.parametrize(
    'DeviceNames, DeviceNodes', [ ('sr0', '/dev/sr0'), ('sr1', '/dev/sr1'),
                                  [ ('sr0', '/dev/sr0'), ('sr3', '/dev/sr3') ] ]
)
def test_detectOpticalDrives(
        monkeypatch,
        configFactory,
        devicesFactory,
        commandFactory,
        DeviceNames,
        DeviceNodes
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: devicesFactory(DeviceNames, DeviceNodes, 'CD')
    )

    Config = configFactory()

    with monkeypatch.context() as M:
        M.setattr('sh.Command', lambda Name: commandFactory(Name, 'password'))

        assert optical.detectOpticalDrives(Config)

        for Device, Name in zip(optical.detectOpticalDrives(Config), DeviceNames):
            assert Device.id == Name

@pytest.mark.parametrize(
    'DiscType,ExpectedType', [
        ('CD', AudioCD), ('DVD', DVD), ('BD', BluRay)
    ]
)
def test_Device_open(
        monkeypatch,
        configFactory,
        devicesFactory,
        DiscIDFactory,
        MBFactory,
        commandFactory,
        DiscType,
        ExpectedType
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: devicesFactory(['sr0'], ['/dev/sr0'], DiscType)
    )

    Config = configFactory()
    DiscID = DiscIDFactory()
    MB = MBFactory()

    with monkeypatch.context() as M:
        M.setattr(
            'musicbrainzngs.get_releases_by_discid',
            lambda *args, **kwargs: MB.info
        )
        M.setattr(
            'discid.read', lambda Device: DiscID
        )
        M.setattr('sh.Command', lambda Name: commandFactory(Name, 'password'))

        assert optical.detectOpticalDrives(Config)

        for Device in optical.detectOpticalDrives(Config):
            assert isinstance(Device.open(), ExpectedType)

def test_Device_open_failure(
        monkeypatch,
        configFactory,
        devicesFactory,
        DiscIDFactory,
        MBFactory,
        commandFactory
):
    monkeypatch.setattr(
        'pyudev.Context.list_devices',
        lambda s, **kwargs: devicesFactory(
            ['sr0', 'sr6'],
            ['/dev/sr0', '/dev/sr6'],
            ''
        )
    )

    Config = configFactory()
    DiscID = DiscIDFactory()
    MB = MBFactory()

    with monkeypatch.context() as M:
        M.setattr(
            'musicbrainzngs.get_releases_by_discid',
            lambda *args, **kwargs: MB.info
        )
        M.setattr(
            'discid.read', lambda Device: DiscID
        )
        M.setattr('sh.Command', lambda Name: commandFactory(Name, 'password'))

        assert optical.detectOpticalDrives(Config)

        for Device in optical.detectOpticalDrives(Config):
            with pytest.raises(RuntimeError):
                Disc = Device.open()
