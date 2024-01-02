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
import logging
from typing import List

import dartt.config as config
import dartt.device as device
import dartt.musicbrainz as mb
import dartt.disc as disc
import dartt.ripper as ripper

class AudioCD(disc.AudioDisc):
    def __init__(self, Dev: device.Device, Musicbrainz: mb.MusicBrainz):
        super().__init__(Dev)
        self._Musicbrainz = Musicbrainz

        logging.debug('Reading disc ID')
        self._DiscIDInfo = discid.read(self._Device.path)
        logging.debug(f'Done reading disc ID: {self._DiscIDInfo}')

        self._DiscInfo = self._Musicbrainz.getDiscInfo(self._DiscIDInfo)
        logging.debug(f'Disc info: {self._DiscInfo}')

    def getTitle(self) -> str:
        return self._DiscInfo.Title

    def getArtists(self) -> List[str]:
        return self._DiscInfo.Artists

    def getTrackInfo(self) -> List[mb.TrackInfo]:
        return self._DiscInfo.Tracks

    def rip(self, Config: config.Config) -> List[disc.AudioTrack]:
        Ripper = ripper.createAudioRipper(Config)
        return Ripper.rip(self)
