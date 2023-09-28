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
        msg: str
) -> bool:
    """Prompt the user with a yes/no question.

    :param msg: The message to print (a ? will be appended)
    :returns: True if the answer is 'yes,' False otherwise

    """
    while True:
        answer = input(f'{msg}? (y/n) ')
        if answer.lower() in ["y","yes"]:
            return True
        elif answer.lower() in ["n","no"]:
            return False

def query(
        msg: str, default: str = None
) -> str:
    """Ask the user for input, providing a default value.

    :param msg: The query message
    :param default: The default value
    :returns: The user's input

    """

    message = f'{msg} [{default}]' if default else msg
    while True:
        result = input(f'{message}: ') or default
        if result:
            return result

def menu(
        msg: str,
        choices: Sequence[str],
        default: str = None
) -> str:
    """Show the user a menu of choices and prompt for input.

    :param msg: The query message
    :param choices: A sequence containing the choices
    :returns: The user's choice

    """

    choices = { k:v for (k,v) in enumerate(choices)}

    default_key = (
        [ k for k,v in choices.items() if v == default ][0] if default else None
    )

    while True:
        for (key, value) in choices.items():
            print(f'[{key}] {value}')

        choice = query(msg, default_key)
        try:
            value = choices[int(choice)]
        except:
            print(f'Invalid choice "{choice}"')
            continue
        return value
