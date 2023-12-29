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

import pytest
from typing import Callable, Dict, Iterable, Sequence

import dartt.musicbrainz as mb

def test_lookup(
        monkeypatch,
        MBFactory,
        DiscIDFactory,
        configFactory,
):
    MB = MBFactory()
    DiscID = DiscIDFactory()
    Config = configFactory()

    with monkeypatch.context() as M:
        M.setattr(
            'musicbrainzngs.get_releases_by_discid',
            lambda *args, **kwargs: MB.info
        )
        M.setattr('sh.Command', lambda name: lambda *args: 'password')

        Info = mb.MusicBrainz(Config).getDiscInfo(DiscID)

        TrackInfo = [f'Track {Track["number"]}: {Track["title"]} - '
                     f'{Track["artist"]}'
                     for Track in MB.releaseTracks()]

        assert str(Info) == (f'Disc ID: {MB.releaseID()} '
                             f'Title: {MB.releaseTitle()} '
                             f'Barcode: {MB.releaseBarcode()} - '
                             f'[\'{MB.releaseArtistName()}\'] - '
                             f'[{", ".join(TrackInfo)}]')
