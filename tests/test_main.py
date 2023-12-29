#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2023-present David A. Greene <dag@obbligato.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dartt.main import main
import logging
import pytest
import sys

def test_main_no_args(
        monkeypatch
):
    with monkeypatch.context() as M:
        # Disable things that need user input or might generate errors.
        M.setattr('dartt.config.readConfig', lambda: None)
        M.setattr('dartt.device.OpticalDrive.open', lambda _: None)
        M.setattr('dartt.device.detectOpticalDrives', lambda _: [])

        main()

@pytest.mark.parametrize(
    'MsgLevel,Expected,Unexpected',
    [ ('debug', [ 'DEBUG', 'INFO', 'WARNING', 'ERROR' ], []),
      ('info', [ 'INFO', 'WARNING', 'ERROR' ], [ 'DEBUG' ]),
      ('warning', [ 'WARNING', 'ERROR' ], [ 'DEBUG', 'INFO' ]),
      ('error', [ 'ERROR' ], [ 'DEBUG', 'INFO', 'WARNING' ]) ]
)
def test_main_msg_level(
        monkeypatch,
        caplog,
        MsgLevel,
        Expected,
        Unexpected
):
    with monkeypatch.context() as M:
        # Make main set the caplog level.
        M.setattr(
            'logging.basicConfig',
            lambda **kwargs: caplog.set_level(getattr(
                logging,
                MsgLevel.upper()
            ))
        )

        # Generate some output
        def genOutput():
            logging.debug('debug')
            logging.info('info')
            logging.warning('warning')
            logging.error('error')

        M.setattr('dartt.config.readConfig', genOutput)

        # Disable things that need user input or might generate errors.
        M.setattr('dartt.device.OpticalDrive.open', lambda _: None)
        M.setattr('dartt.device.detectOpticalDrives', lambda _: [])

        # Set the message level.
        M.setattr('sys.argv', [ sys.argv[0], '--msg-level', MsgLevel])

        main()

    for Text in Expected:
        assert Text in caplog.text

    for Text in Unexpected:
        assert Text not in caplog.text
