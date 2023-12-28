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
            'transcoder': '/usr/bin/flac',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'Very High',
            'ripper': 'makemkvcon',
            'transcoder': 'HandbrakeCLI',
            'archive_output_dir': '/home/me/archive',
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

