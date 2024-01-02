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

from typing import Callable

import dartt.audiocd  as audiocd
import dartt.config as config
import dartt.device as device
import dartt.musicbrainz as mb

def test_audiocd(
        tmp_path,
        monkeypatch,
        configFactory: Callable,
        MBFactory: Callable,
        devicesFactory: Callable,
        DiscIDFactory: Callable,
        commandFactory: Callable,
):
    Config = configFactory()
    DiscID = DiscIDFactory()
    MB = MBFactory()

    with monkeypatch.context() as M:
        M.setattr(
            'pyudev.Context.list_devices',
            lambda s, **kwargs: devicesFactory(
                ('sr0', '/dev/sr0'),
                ('sr0', '/dev/sr0'),
                'CD'
            )
        )
        M.setattr(
            'musicbrainzngs.get_releases_by_discid',
            lambda *args, **kwargs: MB.info
        )
        M.setattr(
            'discid.read', lambda Device: DiscID
        )
        M.setattr('sh.Command', lambda Name: commandFactory(Name, 'password'))

        MBrainz = mb.MusicBrainz(Config)
        Drive = device.detectOpticalDrives(Config)[0]
        CD = audiocd.AudioCD(Drive, MBrainz)

        assert CD.getTitle() == MB.releaseTitle()
        assert CD.getArtists() == [ MB.releaseArtistName() ]
        for Track, MBTrack in zip(CD.getTrackInfo(), MB.releaseTracks()):
            assert Track.Number == MBTrack['number']
            assert Track.Title == MBTrack['title']
            assert Track.Artist == MBTrack['artist']
