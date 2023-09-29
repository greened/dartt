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

from dartt.config import Config
from pathlib import Path
import pytest
import sh
import tomllib
from typing import Callable, Sequence

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
    def makeConfig(ConfigDict: dict) -> Config:
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

@pytest.mark.parametrize(
    'ConfigSubpath, ExpectedConfigSubpath',
    ([ ('', str(Config.defaultUserConfigSubpath)) ] +
#     [])
     [ (str(P), str(P)) for P in Config.userConfigSearchSubpaths ])
)
@pytest.mark.parametrize(
    'AudioQuality, ExpectedAudioQuality',
    ([ ('', Config.defaultQuality) ] +
#     [])
     [ (Quality, Quality) for Quality in Config.qualities ])
)
@pytest.mark.parametrize(
    'AudioRipper, ExpectedAudioRipper',
    ([ ('', Config.defaultAudioRipper) ] +
#     [])
     [ (Ripper, Ripper) for Ripper in Config.audioRippers ])
)
@pytest.mark.parametrize(
    'AudioTranscoder, ExpectedAudioTranscoder',
    ([ ('', Config.defaultAudioTranscoder) ] +
#     [])
     [ (Coder, Coder) for Coder in Config.audioTranscoders ])
)
@pytest.mark.parametrize(
    'AudioTranscodeSubpath, ExpectedAudioTranscodeSubpath',
    [ ('', str(Config.defaultAudioTranscodeSubpath)),
      (str(Config.defaultAudioTranscodeSubpath),
       str(Config.defaultAudioTranscodeSubpath)) ]
)
@pytest.mark.parametrize(
    'VideoQuality, ExpectedVideoQuality',
    ([ ('', Config.defaultQuality) ] +
#     [])
     [ (Quality, Quality) for Quality in Config.qualities ])
)
@pytest.mark.parametrize(
    'VideoRipper, ExpectedVideoRipper',
    ([ ('', Config.defaultVideoRipper) ] +
#     [])
     [ (Ripper, Ripper) for Ripper in Config.videoRippers ])
)
@pytest.mark.parametrize(
    'VideoArchiveSubpath, ExpectedVideoArchiveSubpath',
    [ ('', str(Config.defaultVideoArchiveSubpath)),
      (str(Config.defaultVideoArchiveSubpath),
       str(Config.defaultVideoArchiveSubpath)) ]
)
@pytest.mark.parametrize(
    'VideoTranscoder, ExpectedVideoTranscoder',
    ([ ('', Config.defaultVideoTranscoder) ] +
#     [])
     [ (Coder, Coder) for Coder in Config.videoTranscoders ])
)
@pytest.mark.parametrize(
    'MovieTranscodeSubpath, ExpectedMovieTranscodeSubpath',
    [ ('', str(Config.defaultMovieTranscodeSubpath)),
      (str(Config.defaultMovieTranscodeSubpath),
       str(Config.defaultMovieTranscodeSubpath))]
)
@pytest.mark.parametrize(
    'TVTranscodeSubpath, ExpectedTVTranscodeSubpath',
    [ ('', str(Config.defaultTVTranscodeSubpath)),
      (str(Config.defaultTVTranscodeSubpath),
       str(Config.defaultTVTranscodeSubpath)) ]
)
def test_config_gen(
        tmp_path,
        monkeypatch,
        inputSequenceFactory,
        ConfigSubpath, ExpectedConfigSubpath,
        AudioQuality, ExpectedAudioQuality,
        AudioRipper, ExpectedAudioRipper,
        AudioTranscoder, ExpectedAudioTranscoder,
        AudioTranscodeSubpath, ExpectedAudioTranscodeSubpath,
        VideoQuality, ExpectedVideoQuality,
        VideoRipper, ExpectedVideoRipper,
        VideoArchiveSubpath, ExpectedVideoArchiveSubpath,
        VideoTranscoder, ExpectedVideoTranscoder,
        MovieTranscodeSubpath, ExpectedMovieTranscodeSubpath,
        TVTranscodeSubpath, ExpectedTVTranscodeSubpath
):
    # Force the config to not exist.
    monkeypatch.setattr('pathlib.Path.exists', lambda _: False)

    # Use a fake home directory.
    HomeDir = tmp_path / 'home'
    HomeDir.mkdir()
    monkeypatch.setattr('pathlib.Path.home', lambda: HomeDir)

    # Find all tools.
    monkeypatch.setattr('sh.which', lambda Tool: HomeDir / 'bin' / Tool)

    BaseOutputDir = HomeDir / 'base'
    BaseOutputDir.mkdir()

    def defaultInputOrPath(
            Subpath: str
    ) -> str:
        return ('' if Subpath == ''
                else str(BaseOutputDir / Subpath))

    def getValueKey(
            Value: str,
            Seq: Sequence[str]
    ) -> str:
        Keys = [ f'{K}' for K,V in enumerate(Seq) if V == Value ]
        if Keys:
            return Keys[0]
        return ''

    # Create an input sequence.
    Input = inputSequenceFactory(
        [
            'y',                # Say that we want to create a config.
            getValueKey(
                ConfigSubpath,
                [ str(P) for P in Config.userConfigSearchSubpaths ]
            ),
            str(BaseOutputDir), # Specify base directory.
            getValueKey(AudioRipper, Config.audioRippers),
            getValueKey(AudioTranscoder, Config.audioTranscoders),
            getValueKey(AudioQuality, Config.qualities),
            defaultInputOrPath(AudioTranscodeSubpath),
            getValueKey(VideoRipper, Config.videoRippers),
            defaultInputOrPath(VideoArchiveSubpath),
            getValueKey(VideoTranscoder, Config.videoTranscoders),
            getValueKey(VideoQuality, Config.qualities),
            defaultInputOrPath(MovieTranscodeSubpath),
            defaultInputOrPath(TVTranscodeSubpath)
        ]
    )

    def genInput(Prompt: str):
        print(Prompt)
        return Input.generateInput()

    monkeypatch.setattr('builtins.input', genInput)

    def defaultExpectedOrPath(Subpath: str, DefaultSubpath: str):
        return (str(BaseOutputDir / DefaultSubpath) if Subpath == ''
                else str(BaseOutputDir / Subpath))

    Expected = {
        'base_output_dir': str(BaseOutputDir),
        'audio': {
            'ripper': str(sh.which(ExpectedAudioRipper)),
            'transcoder': str(sh.which(ExpectedAudioTranscoder)),
            'quality': ExpectedAudioQuality,
            'transcode_output_dir': str(BaseOutputDir / ExpectedAudioTranscodeSubpath),
        },
        'video': {
            'ripper': str(sh.which(ExpectedVideoRipper)),
            'archive_output_dir': str(BaseOutputDir / ExpectedVideoArchiveSubpath),
            'transcoder': str(sh.which(ExpectedVideoTranscoder)),
            'quality': ExpectedVideoQuality,
            'movies': {
                'transcode_output_dir': str(BaseOutputDir / ExpectedMovieTranscodeSubpath),
            },
            'tv': {
                'transcode_output_dir': str(BaseOutputDir / ExpectedTVTranscodeSubpath),
            },
        },
    }

    ConfigPath = HomeDir / ExpectedConfigSubpath

    conf = Config()

    with open(ConfigPath, 'rb') as ConfigFile:
        ConfigDict = tomllib.load(ConfigFile)

    assert ConfigDict == Expected

def test_config_dict(
        tmp_path,
        monkeypatch,
        configFactory
):

    ConfigDict = {
        'base_output_dir': '/home/me',
        'audio': {
            'quality': 'High',
            'ripper': '/usr/bin/cdparanoia',
            'transcoder': '/usr/bin/flac',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'Low',
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

    NewConfig = configFactory(ConfigDict)

    assert NewConfig._items == ConfigDict

    DictStack = [ (ConfigDict, NewConfig) ]

    while DictStack:
        Dict, NewDict = DictStack.pop()
        assert Dict.keys() == NewDict.keys()
        assert Dict.items() == NewDict.items()
        for K in Dict.keys():
            if isinstance(Dict[K], dict):
                DictStack.append((Dict[K], NewDict[K]))
                continue
            assert NewDict[K] == Dict[K]
