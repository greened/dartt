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
from collections.abc import Iterable
from contextlib import chdir
import logging
from pathlib import Path
import sh
from tempfile import  TemporaryDirectory
from typing import List

import dartt.config as config
from dartt.disc import AudioDisc, AudioTrack
import dartt.utils as utils

class Ripper(ABC):
    def __init__(
            self,
            Config: config.Config
    ):
        pass

    @abstractmethod
    def rip(self, Disc):
        pass

class AudioRipper(Ripper):
    def __init__(
            self,
            Config: config.Config
    ):
        super().__init__(Config)
        self._ArchivePath = Path(Config.getAudioArchiveDir())

    def rip(self, Disc:  AudioDisc) -> List[AudioTrack]:
        pass

class VideoRipper(Ripper):
    def __init__(
            self,
            Config: config.Config
    ):
        super().__init__(Config)
        self._ArchivePath = Path(Config.getVideoArchiveDir())

class CDParanoiaRipper(AudioRipper):
    def __init__(
            self,
            Config: config.Config
    ):
        super().__init__(Config)
        self.CDParanoia = Config.getAudioRipperCommand()
        self.ArchivePath = Path(Config.getAudioArchiveDir())
        self.Args = [ '--batch', '--stderr-progress' ]

    def rip(self, Disc: AudioDisc) -> List[AudioTrack]:
        # TODO: Make this configurable.
        ArchivePath = (self.ArchivePath / f'{Disc.getArtists()[0]}' /
                       f'{Disc.getTitle()}')

        ArchivePath.mkdir(parents=True, exist_ok=True)

        with TemporaryDirectory() as TempDir:
            with chdir(TempDir):
                print(f'Ripping audio disc "{Disc.getTitle()}"')
                for TrackInfo in Disc.getTrackInfo():
                    print(f'Track {TrackInfo.Number:>02}: {TrackInfo.Title}')

                cmd = sh.Command(self.CDParanoia)
                running = cmd(self.Args, _bg=True, _out=utils.printOutputCallback,
                              _out_bufsize=0, _err=utils.printOutputCallback,
                              _err_bufsize=0)
                running.wait()

            Tracks = []
            for TrackInfo in Disc.getTrackInfo():
                # TODO: Make this configurable.
                RippedPath = (Path(TempDir) /
                              f'track{TrackInfo.Number:>02}.cdda.wav')
                TrackPath = (ArchivePath /
                             f'{TrackInfo.Number:>02}. {TrackInfo.Title}.wav')

                logging.debug(
                    f'RippedPath: {RippedPath} Exists: {RippedPath.exists()}'
                )

                if RippedPath.exists():
                    RippedPath.rename(TrackPath)
                    logging.debug(
                        f'TrackPath: {TrackPath} Exists: {TrackPath.exists()}'
                    )
                    print(f'Ripped {TrackPath}')
                    Tracks.append(AudioTrack(TrackPath, TrackInfo))

        return Tracks

class MakeMKVRipper(VideoRipper):
    def __init__(
            self
    ):
        super().__init__()


def createAudioRipper(Config: config.Config):
    if (Config.getAudioRipperType() == 'cdparanoia'):
        return CDParanoiaRipper(Config)

    raise RuntimeError(f'Unknown audio ripper {Config.getAudioRipperType()}')
