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
import discid
from pathlib import Path
import logging

import dartt.config as config
import dartt.musicbrainz as mb
import dartt.device as device

class Track:
    def __init__(self, Archive: Path):
        self._Archive = Archive

class AudioTrack(Track):
    def __init__(self, ArchivePath: str, TrackInfo: mb.TrackInfo):
        super().__init__(ArchivePath)
        self._TrackInfo = TrackInfo

    @property
    def Number(self):
        return self._TrackInfo.Number

    @property
    def Title(self):
        return self._TrackInfo.Title

    @property
    def Artist(self):
        return self._TrackInfo.Artist

    def __repr__(self) -> str:
        return f'{self._Archive}: {self.Number}. {self.Title} - {self.Artist}'

class VideoTrack(Track):
    def __init__(self, Config):
        pass

class Disc(ABC):
    def __init__(self, Dev: device.Device):
        self._Device = Dev

    def rip(self, Config):
        return []

class AudioDisc(Disc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)

    @abstractmethod
    def getTitle(self):
        pass

    @abstractmethod
    def getArtists(self):
        pass

    @abstractmethod
    def getTrackInfo(self):
        pass

class VideoDisc(Disc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)
