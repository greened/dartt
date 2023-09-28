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

import dartt.utils as utils
import pytest

@pytest.mark.parametrize(
    'value,expected',
    [('y', True), ('Y', True), ('yes', True), ('YES', True), ('n', False),
     ('N', False), ('no', False), ('NO', False)]
)
def test_yesno(
        monkeypatch,
        value,
        expected
):
    monkeypatch.setattr('builtins.input', lambda _: value)
    assert utils.yesno(f'Test {value}') == expected

def test_yesno_loop(
        monkeypatch,
        inputLoopCounterFactory
):
    LoopCounter = inputLoopCounterFactory('bogus', 'y', 1)
    monkeypatch.setattr(
        'builtins.input',
        lambda _, LoopCounter = LoopCounter: LoopCounter.generateInput()
    )

    result = utils.yesno('Test yesno loop')
    assert result == True

    LoopCounter.validate()

@pytest.mark.parametrize(
    'value',
    ['one', 'two', 'three']
)
def test_query(
        monkeypatch,
        capsys,
        value
):
    def inpt(msg, value):
        print(msg)
        return value

    monkeypatch.setattr('builtins.input', lambda _: inpt(_, value))
    result = utils.query(f'{value}')
    captured = capsys.readouterr()
    assert captured.out == f'{value}: \n'
    assert result == value

@pytest.mark.parametrize(
    'value,expected',
    [('', 'default'), ('one', 'one'), ('two', 'two'), ('three', 'three')]
)
def test_query_default(
        monkeypatch,
        capsys,
        value,
        expected
):
    def inpt(msg, value):
        print(msg)
        return value

    monkeypatch.setattr('builtins.input', lambda _: inpt(_, value))
    result = utils.query(f'{value}', 'default')
    captured = capsys.readouterr()
    assert captured.out == f'{value} [default]: \n'
    assert result == expected

@pytest.mark.parametrize(
    'value,expected',
    [('0', 'one'), ('1', 'two'), ('2', 'three')]
)
def test_menu(
        monkeypatch,
        capsys,
        value,
        expected
):
    monkeypatch.setattr('builtins.input', lambda _: value)
    result = utils.menu(f'{value}', ['one', 'two', 'three'])
    captured = capsys.readouterr()
    assert captured.out == '[0] one\n[1] two\n[2] three\n'
    assert result == expected

@pytest.mark.parametrize(
    'value,expected',
    [('', 'two'), ('0', 'one'), ('1', 'two'), ('2', 'three')]
)
def test_menu_default(
        monkeypatch,
        capsys,
        value,
        expected
):
    monkeypatch.setattr('builtins.input', lambda _: value)
    result = utils.menu(f'{value}', ['one', 'two', 'three'], 'two')
    captured = capsys.readouterr()
    assert captured.out == '[0] one\n[1] two\n[2] three\n'
    assert result == expected

def test_menu_loop(
        monkeypatch,
        inputLoopCounterFactory
):
    LoopCounter = inputLoopCounterFactory('9', '2', 1)
    monkeypatch.setattr(
        'builtins.input',
        lambda _, LoopCounter = LoopCounter: LoopCounter.generateInput()
    )

    result = utils.menu(f'Test menu loop', ['one', 'two', 'three'])
    assert result == 'three'

    LoopCounter.validate()
