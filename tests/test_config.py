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

import ast
from dartt.config import Config
from pathlib import Path
import pytest
import sh
import tomllib
from typing import Callable, List, Sequence

def config_gen_test_product(Values: List[List]) -> List[List]:
    # Each outer list is a list of values to be tested.  For each outer list,
    # iterate over its contents holding the other lists to their first element.
    # This is like a Cartesian product if each of the other lists not being
    # iterated were size one.

    NumLists = len(Values)

    OuterResult = []
    for Index in range(NumLists):
        for Value in Values[Index]:
            InnerResult = ()
            for OtherIndex in range(NumLists):
                if OtherIndex != Index:
                    print(f'Appending other inner: {Values[OtherIndex][0]}')
                    InnerResult += Values[OtherIndex][0]
                else:
                    print(f'Appending this inner: {Value}')
                    InnerResult += Value
            print(f'Appending outer: {InnerResult}')
            OuterResult.append(InnerResult)

    print(f'OuterResult: {OuterResult}')
    return OuterResult

@pytest.mark.parametrize(
    'MusicbrainzUser, MusicbrainzPasswordCmd, ExpectedMusicbrainzUser, '
    'ExpectedMusicbrainzPasswordCmd,'

    'ConfigSubpath, ExpectedConfigSubpath,'

    'AudioQuality, ExpectedAudioQuality,'

    'AudioRipper, ExpectedAudioRipper,'

    'AudioArchiveSubpath, ExpectedAudioArchiveSubpath,'

    'AudioTranscoder, ExpectedAudioTranscoder,'

    'AudioTranscodeSubpath, ExpectedAudioTranscodeSubpath,'

    'VideoQuality, ExpectedVideoQuality,'

    'VideoRipper, ExpectedVideoRipper,'

    'VideoArchiveSubpath, ExpectedVideoArchiveSubpath,'

    'VideoTranscoder, ExpectedVideoTranscoder,'

    'MovieTranscodeSubpath, ExpectedMovieTranscodeSubpath,'

    'TVTranscodeSubpath, ExpectedTVTranscodeSubpath',

    config_gen_test_product(
        [
            # Musicbrainz
            [ ('', '', '', ''),
              ('dartt', '', 'dartt', ["pass", "musicbrainz.org/password"]),
              ('dartt', '["otherpass", "mbpass"]', 'dartt', ["otherpass",
                                                             "mbpass"]),
              ('dartt', '["otherpass", {"test": "bogus"}, "mbpass"]', 'dartt',
               ["pass", "musicbrainz.org/password"]),
              ('dartt', 'not non-python code', 'dartt',
               ["pass", "musicbrainz.org/password"]) ],
            # Config subpath
            ([ ('', str(Config.defaultUserConfigSubpath)) ] +
             [ (str(P), str(P)) for P in Config.userConfigSearchSubpaths ]),
            # Audio quality
            ([ ('', Config.defaultQuality) ] +
             [ (Quality, Quality) for Quality in Config.qualities ]),
            # Audio ripper
            ([ ('', Config.defaultAudioRipper) ] +
             [ (Ripper, Ripper) for Ripper in Config.audioRippers ]),
            # Audio archive
            [ ('', str(Config.defaultAudioArchiveSubpath)),
              (str(Config.defaultAudioArchiveSubpath),
               str(Config.defaultAudioArchiveSubpath)) ],
            # Audio transcoder
            ([ ('', Config.defaultAudioTranscoder) ] +
             [ (Coder, Coder) for Coder in Config.audioTranscoders ]),
            # Audio transcode subpath
            [ ('', str(Config.defaultAudioTranscodeSubpath)),
              (str(Config.defaultAudioTranscodeSubpath),
               str(Config.defaultAudioTranscodeSubpath)) ],
            # Video quality
            ([ ('', Config.defaultQuality) ] +
             [ (Quality, Quality) for Quality in Config.qualities ]),
            # Video ripper
            ([ ('', Config.defaultVideoRipper) ] +
             [ (Ripper, Ripper) for Ripper in Config.videoRippers ]),
            # Video archive
            [ ('', str(Config.defaultVideoArchiveSubpath)),
              (str(Config.defaultVideoArchiveSubpath),
               str(Config.defaultVideoArchiveSubpath)) ],
            # Video transcoder
            ([ ('', Config.defaultVideoTranscoder) ] +
             [ (Coder, Coder) for Coder in Config.videoTranscoders ]),
            # Movie transcode subpath
            [ ('', str(Config.defaultMovieTranscodeSubpath)),
              (str(Config.defaultMovieTranscodeSubpath),
               str(Config.defaultMovieTranscodeSubpath))],
            # TV transcode subpath
            [ ('', str(Config.defaultTVTranscodeSubpath)),
              (str(Config.defaultTVTranscodeSubpath),
               str(Config.defaultTVTranscodeSubpath)) ]
        ]
    )
)
def test_config_gen(
        tmp_path,
        monkeypatch,
        inputSequenceFactory,
        MusicbrainzUser, MusicbrainzPasswordCmd,
        ExpectedMusicbrainzUser, ExpectedMusicbrainzPasswordCmd,
        ConfigSubpath, ExpectedConfigSubpath,
        AudioQuality, ExpectedAudioQuality,
        AudioRipper, ExpectedAudioRipper,
        AudioArchiveSubpath, ExpectedAudioArchiveSubpath,
        AudioTranscoder, ExpectedAudioTranscoder,
        AudioTranscodeSubpath, ExpectedAudioTranscodeSubpath,
        VideoQuality, ExpectedVideoQuality,
        VideoRipper, ExpectedVideoRipper,
        VideoArchiveSubpath, ExpectedVideoArchiveSubpath,
        VideoTranscoder, ExpectedVideoTranscoder,
        MovieTranscodeSubpath, ExpectedMovieTranscodeSubpath,
        TVTranscodeSubpath, ExpectedTVTranscodeSubpath
):
    with monkeypatch.context() as M:
        # Force the config to not exist.
        M.setattr('pathlib.Path.exists', lambda _: False)

        # Use a fake home directory.
        HomeDir = tmp_path / 'home'
        HomeDir.mkdir()
        M.setattr('pathlib.Path.home', lambda: HomeDir)

        # Find all tools.
        M.setattr('sh.which', lambda Tool: str(HomeDir / 'bin' / Tool) + '\n')

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

        # No password prompt if no user given.
        MusicbrainzInput = [
            MusicbrainzUser, MusicbrainzPasswordCmd
        ] if len(MusicbrainzUser) > 0 else [ MusicbrainzUser ]

        if len(MusicbrainzInput) > 1 and len(MusicbrainzPasswordCmd) > 0:
            # Prompts a second time if the password command is ill-formed.
            try:
                PassCmdList = ast.literal_eval(MusicbrainzPasswordCmd)
                if (not isinstance(PassCmdList, list) or
                    not all(isinstance(Elem, str) for Elem in PassCmdList)):
                    if len(MusicbrainzInput[0]) > 0:
                        MusicbrainzInput += [
                            '["pass", "musicbrainz.org/password"]'
                        ]
            except:
                if len(MusicbrainzInput[0]) > 0:
                    MusicbrainzInput += [
                        '["pass", "musicbrainz.org/password"]'
                    ]

        Input = inputSequenceFactory(
            [
                'y',                # Say that we want to create a config.
                getValueKey(
                    ConfigSubpath,
                    [ str(P) for P in Config.userConfigSearchSubpaths ]
                )
            ] + MusicbrainzInput +
            [
                str(BaseOutputDir), # Specify base directory.
                getValueKey(AudioRipper, Config.audioRippers),
                defaultInputOrPath(AudioArchiveSubpath),
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

        M.setattr('builtins.input', genInput)

        def defaultExpectedOrPath(Subpath: str, DefaultSubpath: str):
            return (str(BaseOutputDir / DefaultSubpath) if Subpath == ''
                    else str(BaseOutputDir / Subpath))

        Expected = {
            'musicbrainz': {
                'user': ExpectedMusicbrainzUser,
                'password_cmd': ExpectedMusicbrainzPasswordCmd,
            },
            'base_output_dir': str(BaseOutputDir),
            'audio': {
                'ripper': str(sh.which(ExpectedAudioRipper).strip()),
                'archive_output_dir': str(BaseOutputDir / ExpectedAudioArchiveSubpath),
                'transcoder': str(sh.which(ExpectedAudioTranscoder).strip()),
                'quality': ExpectedAudioQuality,
                'transcode_output_dir': str(BaseOutputDir / ExpectedAudioTranscodeSubpath),
            },
            'video': {
                'ripper': str(sh.which(ExpectedVideoRipper).strip()),
                'archive_output_dir': str(BaseOutputDir / ExpectedVideoArchiveSubpath),
                'transcoder': str(sh.which(ExpectedVideoTranscoder).strip()),
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
        'musicbrainz': {
            'user': 'dartt',
            'password_cmd': ["pass", "musicbrainz.org/password"],
        },
        'base_output_dir': '/home/me',
        'audio': {
            'quality': 'High',
            'ripper': '/usr/bin/cdparanoia',
            'archive_output_dir': '/home/me/archive/audio',
            'transcoder': '/usr/bin/flac',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'Low',
            'ripper': '/usr/bin/makemkvcon',
            'transcoder': '/usr/bin/HandbrakeCLI',
            'archive_output_dir': '/home/me/archive/video',
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

def test_write(
        tmp_path,
        monkeypatch,
        configFactory
):
    Config = configFactory()

    ExpectedConfigDict = Config._items

    with monkeypatch.context() as M:
        # Use a fake home directory.  Config constructor should have created it.
        HomeDir = tmp_path / 'home'
        M.setattr('pathlib.Path.home', lambda: HomeDir)

        ConfigPath = HomeDir / Config.defaultUserConfigSubpath

        ConfigPath.parent.mkdir(parents=True)

        Config.write(ConfigPath)

        with open(ConfigPath, 'rb') as ConfigFile:
            ConfigDict = tomllib.load(ConfigFile)

        assert ConfigDict == ExpectedConfigDict

def test_api(
        tmp_path,
        monkeypatch,
        configFactory
):
    Config = configFactory()

    ExpectedAudioRipperType = Path(Config._items['audio']['ripper']).name
    ExpectedAudioRipperCommand = Config._items['audio']['ripper']
    ExpectedAudioTranscoderType = (
        Path(Config._items['audio']['transcoder']).name
    )
    ExpectedAudioTranscoderCommand = Config._items['audio']['transcoder']
    ExpectedAudioArchiveDir = Config._items['audio']['archive_output_dir']
    assert Config.getAudioRipperType() == ExpectedAudioRipperType
    assert Config.getAudioRipperCommand() == ExpectedAudioRipperCommand
    assert Config.getAudioTranscoderType() == ExpectedAudioTranscoderType
    assert Config.getAudioTranscoderCommand() == ExpectedAudioTranscoderCommand
    assert Config.getAudioArchiveDir() == ExpectedAudioArchiveDir

    ExpectedVideoRipperType = Path(Config._items['video']['ripper']).name
    ExpectedVideoRipperCommand = Config._items['video']['ripper']
    ExpectedVideoTranscoderType = (
        Path(Config._items['video']['transcoder']).name
    )
    ExpectedVideoTranscoderCommand = Config._items['video']['transcoder']
    ExpectedVideoArchiveDir = Config._items['video']['archive_output_dir']
    assert Config.getVideoRipperType() == ExpectedVideoRipperType
    assert Config.getVideoRipperCommand() == ExpectedVideoRipperCommand
    assert Config.getVideoTranscoderType() == ExpectedVideoTranscoderType
    assert Config.getVideoTranscoderCommand() == ExpectedVideoTranscoderCommand
    assert Config.getVideoArchiveDir() == ExpectedVideoArchiveDir

def test_reconfig(
        tmp_path,
        monkeypatch,
        configFactory,
        inputSequenceFactory
):
    ConfigDict = {
        'musicbrainz': {
            'user': 'dartt',
            'password_cmd': ["pass", "musicbrainz.org/dartt/password"],
        },
        'base_output_dir': '/home/me',
        'audio': {
            'quality': 'High',
            'ripper': '/usr/bin/cdparanoia',
            'archive_output_dir': '/home/me/archive/audio',
            'transcoder': '/usr/bin/oggenc',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'Low',
            'ripper': '/usr/bin/makemkvcon',
            'transcoder': '/user/bin/HandbrakeCLI',
            'archive_output_dir': '/home/me/archive/video',
            'tv': {
                'transcode_output_dir': '/home/me/movies',
            },
            'movies': {
                'transcode_output_dir': '/home/me/tv',
            }
        }
    }

    NewConfigDict = {
        'musicbrainz': {
            'user': 'dartt',
            'password_cmd': ["pass", "musicbrainz.org/dartt/password"],
        },
        'base_output_dir': '/home/me',
        'audio': {
            'quality': 'Low',
            'ripper': '/usr/bin/cdparanoia',
            'archive_output_dir': '/home/me/archive/audio',
            'transcoder': '/usr/bin/oggenc',
            'transcode_output_dir': '/home/me/music',
        },
        'video': {
            'quality': 'High',
            'ripper': '/usr/bin/makemkvcon',
            'transcoder': '/usr/bin/HandbrakeCLI',
            'archive_output_dir': '/home/me/archive/video',
            'tv': {
                'transcode_output_dir': '/home/me/movies',
            },
            'movies': {
                'transcode_output_dir': '/home/me/tv',
            }
        }
    }

    def getValueKey(
            Value: str,
            Seq: Sequence[str]
    ) -> str:
        Keys = [ f'{K}' for K,V in enumerate(Seq) if V == Value ]
        if Keys:
            return Keys[0]
        return ''

    with monkeypatch.context() as M:
        # Use a fake home directory.
        HomeDir = tmp_path / 'home'

        M.setattr('pathlib.Path.home', lambda: HomeDir)

        NewConfig = configFactory(ConfigDict)

        assert NewConfig._items == ConfigDict

        ConfigPath = HomeDir / Config.defaultUserConfigSubpath

        ConfigPath.parent.mkdir(parents=True)

        NewConfig.write(ConfigPath)

        Input = inputSequenceFactory(
            [
                '',
                '',
                '',
                '',
                '',
                '',
                getValueKey('Low', Config.qualities),
                '',
                '',
                '',
                '',
                getValueKey('High', Config.qualities),
                '',
                ''
            ]
        )

        def genInput(Prompt: str):
            print(Prompt)
            return Input.generateInput()

        M.setattr('builtins.input', genInput)

        # Find all tools.
        M.setattr('sh.which',
                  lambda Tool: str(Path('/usr') / 'bin' / Tool) + '\n')

        NewConfig.reconfig()

    assert NewConfig._items == NewConfigDict
