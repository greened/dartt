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

from typing import Callable, Sequence, Type
import pytest

from dartt.config import Config

class InputLoopCounter:
    """Provide a certain input for some number of input iterations, then change
    it."""
    def __init__(
            self,
            FirstInput: str,
            SecondInput: str,
            Count: int
    ):
        """Construct an InputLoopCounter

        :param FirstInput: Input to return Count times
        :param SecondInput: Input to return after iterating Count times
        :param Count: The number of times to return FirstInput
        :returns: An InputLoopCounter

        """
        self._Value = 0
        self._Count = Count
        self._FirstInput = FirstInput
        self._SecondInput = SecondInput

    @property
    def value(
            self
    ):
        return self._Value

    def generateInput(
            self
    ) -> str:
        """Return input to be consumed, based on the number of times the input
        loop has iterated.

        :returns: The generated input

        """
        self._Value += 1
        return (
            self._FirstInput if self._Value <= self._Count
            else self._SecondInput
        )

    def validate(
            self
    ):
        """Perform test validating after input loop execution.

        :returns: Nothing

        """
        # We return FirstInput _Count times, then one more for the SecondInput.
        assert self.value == self._Count + 1

@pytest.fixture
def inputLoopCounterFactory(
        request
) -> Callable[[str, str, str], InputLoopCounter]:
    """ Return a factory to create an InputLoopCounter.

    :param request: A pytest request object
    :returns: An InputLoopCounter factory

    """
    def makeInputLoopCounter(
            FirstInput: str,
            SecondInput: str,
            Count: int
    ) -> InputLoopCounter:
        """ Create an InputLoopCounter.

        :param FirstInput: The input string to return Count times
        :param SecondInput: The input string to return after Count times
        :param Count: The number of times to return FirstInput
        :returns: An InputLoopCounter

        """
        return InputLoopCounter(FirstInput, SecondInput, Count)

    return makeInputLoopCounter

class InputSequence:
    """Provide a set series of input values."""
    def __init__(
            self,
            Input: Sequence[str],
    ):
        """Construct an InputSequence

        :param Input: Sequence of inputs to generate
        :returns: An InputSequence

        """
        self._Input = Input

    def generateInput(
            self
    ) -> str:
        """Return input to be consumed, based on the given sequence.

        :returns: The generated input

        """
        assert len(self._Input) > 0
        Value = self._Input.pop(0)
        print(f'Generating input "{Value}"')
        return Value

    def validate(
            self
    ):
        """Perform test validating after input loop execution.

        :returns: Nothing

        """
        assert len(self._Input) == 0

@pytest.fixture
def inputSequenceFactory(
        request
) -> Callable[[Sequence[str]], InputSequence]:
    """ Return a factory to create an InputSequence.

    :param request: A pytest request object
    :returns: An InputSequence factory

    """
    def makeInputSequence(
            Input: Sequence[str]
    ) -> InputSequence:
        """ Create an InputSequence.

        :param Input: A sequence of input to generate
        :returns: An InputSequence

        """
        return InputSequence(Input)

    return makeInputSequence

@pytest.fixture
def configFactory(
        monkeypatch,
        tmp_path,
        request
) -> Callable[[dict], Config]:
    """ Return a factory to create a Config.

    :param monkeypatch: A monkeypatcher
    :param tmp_path: A pytest tmp_path object
    :param request: A pytest request object
    :returns: A Config factory

    """
    DefaultConfig = {
        'musicbrainz': {
            'user': 'dartt',
            'password_cmd': ["pass", "musicbrainz.org/password"],
        },
        'base_output_dir': '/home/me',
        'audio': {
            'quality': 'Very High',
            'ripper': '/usr/bin/cdparanoia',
            'archive_output_dir': '/home/me/archive/audio',
            'transcoder': '/usr/bin/flac',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'Very High',
            'ripper': 'makemkvcon',
            'archive_output_dir': '/home/me/archive/video',
            'transcoder': 'HandbrakeCLI',
            'tv': {
                'transcode_output_dir': '/home/me/movies',
            },
            'movies': {
                'transcode_output_dir': '/home/me/tv',
            }
        }
    }

    def makeConfig(ConfigDict: dict = DefaultConfig) -> Config:
        """ Create an InputSequence.

        :param ConfigDict: A dict of config values
        :returns: A Config

        """
        with monkeypatch.context() as M:
            # Force the config to not exist.
            M.setattr('pathlib.Path.exists', lambda _: False)

            # Use a fake home directory.
            HomeDir = tmp_path / 'home'
            HomeDir.mkdir()
            M.setattr('pathlib.Path.home', lambda: HomeDir)

            # Do not prompt for config values.
            M.setattr('builtins.input', lambda _: 'n')

            NewConfig = Config()

        NewConfig._items.update(ConfigDict)

        return NewConfig

    return makeConfig

class MockMB:
    @classmethod
    def releaseID(
            cls
    ):
        return 'release-id'

    @classmethod
    def releaseTitle(
            cls
    ):
        return 'A Great Release'

    @classmethod
    def releaseDate(
            cls
    ):
        return 'Yesterday'

    @classmethod
    def releaseBarcode(
            cls
    ):
        return 'ba7c0de'

    @classmethod
    def releaseArtistName(
            cls
    ):
        return 'A. Great Artist'

    @classmethod
    def releaseTracks(
            cls
    ):
        return [
            {
                'number': 0,
                'length': 20,
                'title': 'Track 0',
                'artist': 'AGA & Her Band',
            },
            {
                'number': 1,
                'length': 30,
                'title': 'Track 1',
                'artist': 'AGA & Her Band',
            }
        ]

    def __init__(
            self
    ):
        self._Releases = [
            {
                'id': self.releaseID(),
                'title': self.releaseTitle(),
                'date': self.releaseDate(),
                'barcode': self.releaseBarcode(),
                'artist-credit': [
                    {
                        'artist': {
                            'name': self.releaseArtistName(),
                        },
                    }
                ],
                'medium-list': [
                    {
                        'track-list': [
                        ]
                    }
                ],
            }
        ]
        for Track in self.releaseTracks():
            self._Releases[0]['medium-list'][0]['track-list'].append(
                {
                    'number': Track['number'],
                    'length': Track['length'],
                    'recording': {
                        'length': Track['length'],
                        'title': Track['title'],
                        'artist-credit-phrase': Track['artist']
                    }
                }
            )

        self._Disc = {
            'disc': {
                'sectors': 132,
                'offset-list': [0, 12],
                'offset-count': 2,
                'release-list': self._Releases
            }
        }

    @property
    def info(
            self
    ) -> dict:
        return self._Disc

@pytest.fixture
def MBFactory(
        request
) -> Callable[[], MockMB]:
    def makeMB() -> MockMB:
        return MockMB()

    return makeMB

class MockDiscID:
    def __init__(self):
        self._ID = 'frobnitz'
        self._TOC = 'weevoo'

    @property
    def id(self):
        return self._ID

    @property
    def toc_string(self):
        return self._TOC

@pytest.fixture
def DiscIDFactory(
        request
) -> Callable[[], MockDiscID]:
    def makeDiscID() -> MockDiscID:
        return MockDiscID()

    return makeDiscID

@pytest.fixture
def commandFactory(
        request
) -> Callable[[str, str], Type]:
    def makeCommand(Command: str, Output: str) -> Type:
        class MockCommand:
            def __init__(self, Cmd: str):
                self._Cmd = Cmd
                self._Output = Output

            def __call__(self, *Args) -> str:
                return self._Output

        return MockCommand

    return makeCommand
