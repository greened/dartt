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

import discid
import logging
import musicbrainzngs as mb
import sh

import dartt.config as config

class TrackInfo:
    def __init__(
            self,
            Info: dict
    ):
        self._Number = Info['number']
        self._Length = Info.get('length', None)
        Recording = Info['recording']
        if not self._Length:
            self._Length = Recording.get('length', None)
        self._Title = Recording['title']
        self._Artist = Recording['artist-credit-phrase']


    def __repr__(self):
        return f'Track {self._Number}: {self._Title} - {self._Artist}'

class DiscInfo:
    def __init__(
            self,
            Info: dict
    ):
        self._Sectors = None
        self._Offsets = None
        self._TrackCount = None
        self._ID = None
        self._Date = None
        self._Artists = []
        self._Title = None
        self._Tracks = []
        self._Barcode = None

        logging.debug(f'MB info: {Info}')

        def processReleases(Releases: dict):
            assert len(Releases) == 1, "Unexpected multiple releases"

            self._ID = Releases[0]['id']
            self._Title = Releases[0]['title']
            self._Date = Releases[0]['date']
            ArtistCredits = Releases[0]['artist-credit']
            for Artist in ArtistCredits:
                self._Artists.append(Artist['artist']['name'])

            Barcode = Releases[0].get('barcode', None)
            if Barcode:
                self._Barcode = Barcode

            TrackList = []
            for Medium in Releases[0]['medium-list']:
                for Track in Medium['track-list']:
                    TrackList.append(TrackInfo(Track))

            if TrackList:
                self._Tracks = TrackList

        Disc = Info.get('disc', None)

        if Disc:
            self._Sectors = Disc['sectors']
            self._Offsets = Disc.get('offset-list', [])
            self._Offsets = Disc.get('offset-count', None)

            self._Releases = Disc['release-list']
            processReleases(self._Releases)
            return

        CDStub = Info.get('cdstub', None)
        if CDStub:
            logging.debug(f'CD stub: {CDStub}')
            self._Artist = CDStub['artist']
            self._Title = CDStub['title']
            Barcode = CDStub.get('barcode', None)
            if Barcode:
                self._Barcode = Barcode
            return

        ReleaseList = Info.get('release-list', None)
        if ReleaseList:
            logging.debug(f'Release list: {ReleaseList}')
            self._Releases = ReleaseList
            processReleases(self._Releases)
            return

    def __repr__(self):
        return (f'Disc ID: {self._ID} Title: {self._Title} '
                f'Barcode: {self._Barcode} - {self._Artists} - {self._Tracks}')

class MusicBrainz:
    def __init__(
            self,
            Config: config.Config
    ):
        self._Config = Config['musicbrainz']
        self._Authenticated = False
        self.authenticate()
        mb.set_useragent('dartt', '0.0.1', 'dag@obbligato.org')

    def authenticate(
            self
    ):
        User= self._Config.get('user', None)

        if User:
            PassCmd = self._Config['password_cmd']

            Cmd = sh.Command(
                PassCmd[0]
            )

            Password = Cmd(
                *PassCmd[1:]
            )

            mb.auth(User, Password)

    def getDiscInfo(
            self,
            Disc: discid.Disc
    ) -> DiscInfo:
        logging.debug(f'discid: {Disc.id}')

        try:
            Releases = mb.get_releases_by_discid(
                Disc.id,
                toc=Disc.toc_string,
                includes=['artist-credits', 'recordings']
            )
            return DiscInfo(Releases)
        except mb.WebServiceError as Error:
            logging.error(f'Musicbainz error: {Error}')
            return DiscInfo(dict())
