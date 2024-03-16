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

"""
Utility functions for common tasks.
"""

from collections.abc import Mapping, Sequence

def yesno(
        Msg: str
) -> bool:
    """Prompt the user with a yes/no question.

    :param Msg: The message to print (a ? will be appended)
    :returns: True if the answer is 'yes,' False otherwise

    """
    while True:
        Answer = input(f'{Msg}? (y/n) ').strip()
        if Answer.lower() in ["y","yes"]:
            return True
        elif Answer.lower() in ["n","no"]:
            return False

def query(
        Msg: str,
        Default: str = None
) -> str:
    """Ask the user for input, providing a default value.

    :param Msg: The query message
    :param Default: The default value
    :returns: The user's input

    """

    Message = (f'{Msg} [{Default}]' if Default is not None and len(Default) > 0
               else Msg)
    while True:
        Result = input(f'{Message}: ').strip() or Default
        if Result:
            return Result

def menu(
        Msg: str,
        Choices: Sequence[str],
        Default: str = None
) -> str:
    """Show the user a menu of choices and prompt for input.

    :param Msg: The query message
    :param Choices: A sequence containing the choices
    :returns: The user's choice

    """

    Choices = { K:V for (K,V) in enumerate(Choices) }

    DefaultKey = None
    if Default is not None and len(Default) > 0:
        Keys = [ f'{K}' for K,V in Choices.items() if V == Default ]
        assert len(Keys) == 1, f'{len(Keys)} matches to {Default}'
        DefaultKey = Keys[0]

    while True:
        for (Key, Value) in Choices.items():
            print(f'[{Key}] {Value}')

        Choice = query(Msg, DefaultKey)
        try:
            Value = Choices[int(Choice)]
        except:
            print(f'Invalid choice "{Choice}"')
            continue
        return Value
