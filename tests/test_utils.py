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
    'Value,Expected',
    [('y', True), ('Y', True), ('yes', True), ('YES', True), ('n', False),
     ('N', False), ('no', False), ('NO', False)]
)
def test_yesno(
        monkeypatch,
        Value,
        Expected
):
    monkeypatch.setattr('builtins.input', lambda _: Value)
    assert utils.yesno(f'Test {Value}') == Expected

def test_yesno_loop(
        monkeypatch,
        inputLoopCounterFactory
):
    LoopCounter = inputLoopCounterFactory('bogus', 'y', 1)
    monkeypatch.setattr(
        'builtins.input',
        lambda _, LoopCounter = LoopCounter: LoopCounter.generateInput()
    )

    Result = utils.yesno('Test yesno loop')
    assert Result == True

    LoopCounter.validate()

@pytest.mark.parametrize(
    'Value',
    ['one', 'two', 'three']
)
def test_query(
        monkeypatch,
        capsys,
        Value
):
    def inpt(msg, Value):
        print(msg)
        return Value

    monkeypatch.setattr('builtins.input', lambda _: inpt(_, Value))
    Result = utils.query(f'{Value}')
    Captured = capsys.readouterr()
    assert Captured.out == f'{Value}: \n'
    assert Result == Value

@pytest.mark.parametrize(
    'Default',
    [ 'default', 'one', 'two', 'three', '0', '1', '2']
)
@pytest.mark.parametrize(
    'Value',
    [ '', 'one', 'two', 'three', '0', '1', '2' ]
)
def test_query_default(
        monkeypatch,
        capsys,
        Default,
        Value
):
    def inpt(msg, Value):
        print(msg)
        return Value

    monkeypatch.setattr('builtins.input', lambda _: inpt(_, Value))

    Expected = Value if Value != '' else Default
    Result = utils.query(f'{Value}', Default)
    Captured = capsys.readouterr()
    assert Captured.out == f'{Value} [{Default}]: \n'
    assert Result == Expected

@pytest.mark.parametrize(
    'Value,Expected',
    [('0', 'one'), ('1', 'two'), ('2', 'three')]
)
def test_menu(
        monkeypatch,
        capsys,
        Value,
        Expected
):
    monkeypatch.setattr('builtins.input', lambda _: Value)
    Result = utils.menu(f'{Value}', ['one', 'two', 'three'])
    Captured = capsys.readouterr()
    assert Captured.out == f'[0] one\n[1] two\n[2] three\n'
    assert Result == Expected

@pytest.mark.parametrize(
    'Default',
    [ 'one', 'two', 'three']
)
@pytest.mark.parametrize(
    'Value,Expected',
    [('', ''), ('0', 'one'), ('1', 'two'), ('2', 'three')]
)
def test_menu_default(
        monkeypatch,
        capsys,
        Default,
        Value,
        Expected
):
    if Value == '':
        Expected = Default

    monkeypatch.setattr('builtins.input', lambda _: Value)
    Result = utils.menu(f'{Value}', ['one', 'two', 'three'], Default)
    Captured = capsys.readouterr()
    assert Captured.out == '[0] one\n[1] two\n[2] three\n'
    assert Result == Expected

def test_menu_loop(
        monkeypatch,
        inputLoopCounterFactory
):
    LoopCounter = inputLoopCounterFactory('9', '2', 1)
    monkeypatch.setattr(
        'builtins.input',
        lambda _, LoopCounter = LoopCounter: LoopCounter.generateInput()
    )

    Result = utils.menu(f'Test menu loop', ['one', 'two', 'three'])
    assert Result == 'three'

    LoopCounter.validate()
