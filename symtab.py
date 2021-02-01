# -*- coding: utf-8 -*-

from enum import Enum
from typing import Optional, Union

ENABLE_COLOR = True


def colored(s: str, color: str):
    if not ENABLE_COLOR:
        return s
    if color == 'red':
        return f'\033[31m{s}\033[0m'
    if color == 'yellow':
        return f'\033[33m{s}\033[0m'
    if color == 'green':
        return f'\033[32m{s}\033[0m'
    return s


class Scope(Enum):
    LOCAL = 0
    GLOBAL = 1
    FUNC = 2
    CONSTANT = 3

    def __str__(self) -> str:
        if self == Scope.LOCAL:
            return 'LOCAL'
        if self == Scope.GLOBAL:
            return 'GLOBAL'
        if self == Scope.FUNC:
            return 'FUNC'
        if self == Scope.CONSTANT:
            return 'CONSTANT'
        return super().__str__()

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_str(cls, v):
        if v == "local":
            return cls.LOCAL
        if v == 'global':
            return cls.GLOBAL
        if v == 'proc':
            return cls.FUNC
        raise ValueError(f'KeyError: {v}')


class Symbol(object):
    def __init__(self, name: str, scope: Scope, register: int = None):
        super().__init__()
        self.name = name
        self.register = register
        self.scope = scope

    def __str__(self) -> str:
        return f'<"{self.name}"|{self.register}|{self.scope}>'

    def __repr__(self) -> str:
        return self.__str__()


class SymbolTable(object):
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.local_depth = 0

    def insert(self, token: str, scope: Optional[Union[Scope, str]] = None, register: int = None):
        scope = scope or self.scope()
        if type(scope) is str:
            scope = Scope.from_str(scope)

        if scope == Scope.LOCAL:
            assert register is not None
            symbol = Symbol(token, scope=scope, register=register)
        else:
            symbol = Symbol(token, scope=scope)

        self.symbols.append(symbol)

        print(f'{colored("追加", "yellow")}: {symbol},\t現在のシンボルの数: {len(self.symbols)}')

    def lookup(self, token: str) -> Symbol:
        found = [r for r in self.symbols if r.name == token]
        if not len(found) > 0:
            print('構文エラー: トークンなし')
            print([r for r in self.symbols])
            exit()

        print(f'{colored("検索", "green")}: {found[-1]}')
        return found[-1]

    def remove_local_var(self):
        self.symbols = [s for s in self.symbols if s.scope != Scope.LOCAL]
        print(f'{colored("削除", "red")}: 現在のシンボル {self.symbols}')

    def scope(self):
        if self.local_depth > 0:
            return Scope.LOCAL
        return Scope.GLOBAL

    def increase_depth(self):
        self.local_depth += 1

    def decrease_depth(self):
        if not self.local_depth > 0:
            print('構文エラー: 階層が誤っています')
            exit()
        self.local_depth -= 1
