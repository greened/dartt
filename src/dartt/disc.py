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

import dartt.device as device
import dartt.musicbrainz as mb

class Disc(ABC):
    def __init__(self, Dev: device.Device):
        self._Device = Dev

class AudioDisc(Disc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)

class VideoDisc(Disc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)

class AudioCD(AudioDisc):
    def __init__(self, Dev: device.Device, Musicbrainz: mb.MusicBrainz):
        super().__init__(Dev)
        self._Musicbrainz = Musicbrainz

        logging.debug('Reading disc ID')
        self._DiscIDInfo = discid.read(self._Device.path)
        logging.debug(f'Done reading disc ID: {self._DiscIDInfo}')

        Info = self._Musicbrainz.getDiscInfo(self._DiscIDInfo)
        logging.debug(f'Disc info: {Info}')

class DVD(VideoDisc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)

class BluRay(VideoDisc):
    def __init__(self, Dev: device.Device):
        super().__init__(Dev)
