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

import logging
from pathlib import Path
import sh
import tomli_w
import tomllib

import dartt.utils as utils

"""Configuration for dartt"""

class Config:
    """Hold all config values from both config files and any command-line
    options.  Values are accessed with a dictionary-like interface.  This
    dictionary is described by a TOML config file.

    """

    @classmethod
    @property
    def userConfigSearchSubpaths(cls):
        """ Return the possible subpaths for user's config under $HOME.

        :param cls: The Config class
        :returns: The subpaths to search for the user's config

        """
        return [ Path('.config') / 'dartt' / 'config.toml',
                 Path('.dartt') / 'config.toml' ]

    @classmethod
    @property
    def defaultUserConfigSubpath(cls):
        """ Return the defaul subpath for user's config under $HOME.

        :param cls: The Config class
        :returns: The default subpath to search for the user's config

        """
        return cls.userConfigSearchSubpaths[0]

    @classmethod
    @property
    def configSearchPaths(cls):
        """ Return all possible paths for config files.

        :param cls: The Config class
        :returns: All paths to search for configs

        """
        return ([ Path('/etc/dartt/config.toml') ] +
                [ Path.home() / subpath
                  for subpath in cls.userConfigSearchSubpaths])

    @classmethod
    @property
    def qualities(cls):
        """ Return all transcoding qualities.

        :param cls: The Config class
        :returns: The supported transcoding qualities

        """
        return [ 'Very High', 'High', 'Medium', 'Low' ]

    @classmethod
    @property
    def defaultQuality(cls):
        """ Return the default transcoding quality.

        :param cls: The Config class
        :returns: The default transcoding quality

        """
        return 'Very High'

    @classmethod
    @property
    def audioRippers(cls):
        """ Return all supported audio rippers.

        :param cls: The Config class
        :returns: Supported audio rippers

        """
        return [ 'cdparanoia' ]

    @classmethod
    @property
    def defaultAudioRipper(cls):
        """ Return the default audio ripper.

        :param cls: The Config class
        :returns: The default audio ripper

        """
        return cls.audioRippers[0]

    @classmethod
    @property
    def audioTranscoders(cls):
        """ Return all supported audio transcoders.

        :param cls: The Config class
        :returns: Supported audio transcoders

        """
        return [ 'fdkaac', 'ffmpeg', 'flac', 'lame', 'mac', 'mpcenc', 'oggenc',
                 'twolame', 'tta', 'wavpack' ]

    @classmethod
    @property
    def defaultAudioTranscoder(cls):
        """ Return the default audio transcoder.

        :param cls: The Config class
        :returns: The default audio transcoder

        """
        return cls.audioTranscoders[2]

    @classmethod
    @property
    def defaultAudioTranscodeSubpath(cls):
        """ Return the default subpath under the base path for transcoded audio.

        :param cls: The Config class
        :returns: The default subpath for transcoded audio

        """
        return Path('music')

    @classmethod
    @property
    def videoRippers(cls):
        """ Return all supported video rippers.

        :param cls: The Config class
        :returns: Supported video rippers

        """
        return [ 'makemkvcon' ]

    @classmethod
    @property
    def defaultVideoRipper(cls):
        """ Return the default video ripper.

        :param cls: The Config class
        :returns: The default video ripper

        """
        return cls.videoRippers[0]

    @classmethod
    @property
    def defaultVideoArchiveSubpath(cls):
        """ Return the default subpath under the base path for archived video.

        :param cls: The Config class
        :returns: The default subpath for archived video

        """
        return Path('archive') / 'video'

    @classmethod
    @property
    def videoTranscoders(cls):
        """ Return all supported video transcoders.

        :param cls: The Config class
        :returns: Supported video transcoders

        """
        return [ 'HandbrakeCLI' ]

    @classmethod
    @property
    def defaultVideoTranscoder(cls):
        """ Return the default video transcoder.

        :param cls: The Config class
        :returns: The default video transcoder

        """
        return cls.videoTranscoders[0]

    @classmethod
    @property
    def defaultMovieTranscodeSubpath(cls):
        """Return the default subpath under the base path for transcoded
        movies.

        :param cls: The Config class
        :returns: The default subpath for transcoded movies

        """
        return Path('video') / 'movies'

    @classmethod
    @property
    def defaultTVTranscodeSubpath(cls):
        """Return the default subpath under the base path for transcoded
        television shows.

        :param cls: The Config class
        :returns: The default subpath for transcoded television shows

        """
        return Path('video') / 'tv'

    def __init__(self):
        """Construct a Config object.  This reads config items from a hierarchy
        of files, with later reads overwriting values from earlier reads.  The
        read order is:

        /etc/dartt/config.toml
        $HOME/.dartt/config.toml
        $HOME/.config/dartt/config.toml

        :returns: A Config object

        """

        self._items = dict()

        if not any(Config.exists() for Config in self.configSearchPaths):
            if utils.yesno('No configuration found, create one'):
                self._update(*self._create())

        for Config in self.configSearchPaths:
            if Config.exists():
                self._items.update(tomllib.load(Config))

    def _update(self, ConfigDict, ConfigPath):
        """Update the config file in the user's home directory.

        :returns: Dictionary containing the updated config contents
        """

        def found(Command: str):
            try:
                sh.which(Command)
            except sh.ErrorReturnCode_1:
                return False
            return True

        BaseOutputDirectory = ''
        while not BaseOutputDirectory:
            BaseOutputDirectory = input('Base output directory: ')
        ConfigDict['base_output_dir'] = BaseOutputDirectory

        AudioRippers = [Audio for Audio in self.audioRippers if found(Audio)]
        if AudioRippers:
            DefaultAudioRipper = (self.defaultAudioRipper
                                  if self.defaultAudioRipper in AudioRippers
                                  else AudioRippers[0])
            ConfigDict['audio']['ripper'] = str(sh.which(
                utils.menu(
                    'Default audio ripper', AudioRippers, DefaultAudioRipper
                )
            ))

        AudioTranscoders = [Coder for Coder in self.audioTranscoders
                            if found(Coder)]
        if AudioTranscoders:
            DefaultTranscoder = (self.defaultAudioTranscoder
                                 if self.defaultAudioTranscoder
                                 in AudioTranscoders
                                 else AudioTranscoders[0])
            ConfigDict['audio']['transcoder'] = str(sh.which(
                utils.menu(
                    'Default audio transcoder',
                    AudioTranscoders,
                    DefaultTranscoder
                )
            ))

            ConfigDict['audio']['quality'] = (
                utils.menu(
                    'Default audio quality',
                    self.qualities,
                    self.defaultQuality
                )
            )

            DefaultTranscodeDir = (Path(ConfigDict['base_output_dir']) /
                                   self.defaultAudioTranscodeSubpath)
            ConfigDict['audio']['transcode_output_dir'] = (
                utils.query(
                    'Default audio transcode directory',
                    str(DefaultTranscodeDir)
                )
            )

        VideoRippers = [Video for Video in self.videoRippers if found(Video)]
        if VideoRippers:
            DefaultVideoRipper = (self.defaultVideoRipper
                                  if self.defaultVideoRipper in VideoRippers
                                  else VideoRippers[0])
            ConfigDict['video']['ripper'] = str(sh.which(
                utils.menu(
                    'Default video ripper',
                    VideoRippers,
                    DefaultVideoRipper
                )
            ))

            DefaultArchiveOutputDirectory = (
                ConfigDict['base_output_dir'] / self.defaultVideoArchiveSubpath
            )
            ConfigDict['video']['archive_output_dir'] = (
                utils.query(
                    'Archive directory',
                    str(DefaultArchiveOutputDirectory)
                )
            )

        VideoTranscoders = [Coder for Coder in self.videoTranscoders
                            if found(Coder)]
        if VideoTranscoders:
            DefaultTranscoder =  (self.defaultVideoTranscoder
                                  if self.defaultVideoTranscoder in
                                  VideoTranscoders else VideoTranscoders[0])
            ConfigDict['video']['transcoder'] = str(sh.which(
                utils.menu(
                    'Default video transcoder',
                    VideoTranscoders,
                    DefaultTranscoder
                )
            ))

            ConfigDict['video']['quality'] = (
                utils.menu(
                    'Default video quality',
                    self.qualities,
                    self.defaultQuality
                )
            )

            DefaultTranscodeDir = (Path(ConfigDict['base_output_dir']) /
                                   self.defaultMovieTranscodeSubpath)
            ConfigDict['video']['movies']['transcode_output_dir'] = (
                utils.query(
                    'Default movie transcode directory',
                    str(DefaultTranscodeDir)
                )
            )

            DefaultTranscodeDir = (Path(ConfigDict['base_output_dir']) /
                                   self.defaultTVTranscodeSubpath)
            ConfigDict['video']['tv']['transcode_output_dir'] = (
                utils.query(
                    'Default TV transcode directory',
                    str(DefaultTranscodeDir)
                )
            )

            with open(ConfigPath, 'wb') as ConfigFile:
                tomli_w.dump(ConfigDict, ConfigFile)

    def _create(self):
        """Create an empty config file.

        :returns: Tuple of a dictionary containing the empty config contents and
        the path to the created config file

        """

        ConfigPath = Path(utils.menu(
            'Config file location',
            [ str(Path.home() / Subpath)
              for Subpath in self.userConfigSearchSubpaths ],
            str(Path.home() / self.defaultUserConfigSubpath)
        ))

        ConfigDict = {
            'base_output_dir': '',
            'audio': {
                'quality': '',
                'ripper': '',
                'transcoder': '',
                'transcode_output_dir': '',
            },
            'video': {
                'quality': '',
                'ripper': '',
                'transcoder': '',
                'archive_output_dir': '',
                'tv': {
                    'transcode_output_dir': '',
                },
                'movies': {
                    'transcode_output_dir': '',
                }
            }
        }

        ConfigPath.parent.mkdir(exist_ok=True, parents=True)

        with open(ConfigPath, 'wb') as ConfigFile:
            tomli_w.dump(ConfigDict, ConfigFile)

        with open(ConfigPath, 'rb') as ConfigFile:
            return (tomllib.load(ConfigFile), ConfigPath)

    def __setitem__(self, key, item):
        self._items[key] = item

    def __getitem__(self, key):
        return self._items[key]

    def __repr__(self):
        return repr(self._items)

    def __len__(self):
        return len(self._items)

    def __delitem__(self, key):
        del self._items[key]

    def copy(self):
        return self._items.copy()

    def has_key(self, k):
        return k in self._items

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return self._items.items()

    def __cmp__(self, dict_):
        return self.__cmp__(self._items, dict_)

    def __contains__(self, item):
        return item in self._items

    def __iter__(self):
        return iter(self._items)

    def __unicode__(self):
        return unicode(repr(self._items))



def readConfig():
    return Config()
