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

from pathlib import Path
import sh
from typing import Callable, Dict, Iterable, Sequence

import dartt.audiocd as audiocd
import dartt.musicbrainz as mb
import dartt.optical as optical
from dartt.ripper import CDParanoiaRipper

class MockRipper:
    def __init__(self, CD: audiocd.AudioCD, RipPath: Path):
        self.CD  = CD
        self.RipPath = RipPath

    def __call__(self, *Args):
        for Track in self.CD.getTrackInfo():
            File = Path.cwd() / f'track{Track.Number:02}.cdda.wav'
            print(f'Ripping to {File}')
            File.touch()

def test_rip(
        tmp_path,
        monkeypatch,
        configFactory,
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
        Drive = optical.detectOpticalDrives(Config)[0]
        CD = audiocd.AudioCD(Drive, MBrainz)
        CDTracks =  CD.getTrackInfo()

        ripper = CDParanoiaRipper(Config)

        RipPath = Path(Config.getAudioArchiveDir())

        M.setattr(
            'sh.Command',
            lambda Name: (MockRipper(CD, RipPath)
                          if Name == '/usr/bin/cdparanoia' else
                          commandFactory(Name, 'password')))

        RippedTracks = ripper.rip(CD)

        assert len(RippedTracks) == len(CDTracks)

        for RippedTrack, CDTrack in zip(RippedTracks, CDTracks):
            ExpectedPath = (RipPath / f'{CD.getArtists()[0]}' /
                            f'{CD.getTitle()}' /
                            f'{CDTrack.Number:02}. {CDTrack.Title}.wav')
            assert RippedTrack.RippedPath == ExpectedPath
            assert RippedTrack.Number == CDTrack.Number
            assert RippedTrack.Title ==  CDTrack.Title
            assert RippedTrack.Artist == CDTrack.Artist

