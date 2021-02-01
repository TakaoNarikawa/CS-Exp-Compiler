# -*- coding: utf-8 -*-

from enum import Enum
from typing import Optional, Union, List

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
    def __init__(self, name: str, scope: Scope, register: int = None, args_cnt: int = 0):
        super().__init__()
        self.name = name
        self.register = register
        self.scope = scope
        self.args_cnt = args_cnt

    def __str__(self) -> str:
        name_suffix = f"({self.args_cnt})" if self.scope == Scope.FUNC else ""
        return f'<"{self.name}{name_suffix}"|{self.register}|{self.scope}>'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.name == other.name and \
            self.register == other.register and \
            self.scope == other.scope and \
            self.args_cnt == other.args_cnt


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

    def lookup(self, token: str, scope_condition: Optional[List[Scope]] = None, args_cnt: int = None) -> Symbol:
        found = [
            r for r in self.symbols
            if r.name == token and (args_cnt is None or r.args_cnt == args_cnt) and \
                (scope_condition is None or r.scope in scope_condition)
        ]
        if not len(found) > 0:
            raise RuntimeError(f'構文エラー: トークンなし ... {token}')

        print(f'{colored("検索", "green")}: {found[-1]}')
        return found[-1]

    def update_args_cnt(self, symbol, cnt):
        found = [i for i, s in enumerate(self.symbols) if s == symbol]
        if not len(found) > 0:
            raise RuntimeError("シンボルが見つかりませんでした。")
        index = found[0]

        new_symbol = Symbol(name=symbol.name, scope=symbol.scope, register=symbol.register, args_cnt=cnt)
        if new_symbol not in self.symbols:
            self.symbols[index].args_cnt = cnt
        else:
            # 更新先の内容がすでに存在する場合は、削除する
            self.symbols.pop(index)
            

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
