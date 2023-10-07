#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2023-present David A. Greene <dag@obbligato.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import dartt
from dartt.main import main
import logging
import pytest

def test_main_no_args(
        monkeypatch
):
    # Disable things that need user input or might generate errors.
    monkeypatch.setattr('dartt.main.readConfig', lambda: None)
    monkeypatch.setattr('dartt.device.OpticalDrive.open', lambda _: None)

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
    # Make main set the caplog level.
    monkeypatch.setattr(
        'logging.basicConfig',
        lambda **kwargs: caplog.set_level(getattr(logging, MsgLevel.upper()))
    )

    # Generate some output
    def genOutput():
        logging.debug('debug')
        logging.info('info')
        logging.warning('warning')
        logging.error('error')

    monkeypatch.setattr('dartt.main.readConfig', genOutput)

    # Disable things that need user input or might generate errors.
    monkeypatch.setattr('dartt.device.OpticalDrive.open', lambda _: None)

    main(['--msg-level', MsgLevel])

    for Text in Expected:
        assert Text in caplog.text

    for Text in Unexpected:
        assert Text not in caplog.text
