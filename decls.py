# -*- coding: utf-8 -*-

from typing import List, Optional

from symtab import Scope
from llvmcodes import LLVMCode


class Fundecl(object):
    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.codes: List[LLVMCode] = []
        self.args_cnt = 0
        self.cntr = 1 # レジスタカウンター
        self.rettype = "i32"
        self.is_func = False

    def register(self):
        t = self.cntr
        self.cntr += 1
        return t

    def to_string(self):
        as_function = self.name is not None and len(self.name) > 0
        statements = [str(code) for code in self.codes]
        if as_function:
            statements = [with_indent(s, 2) for s in statements]

        arg_types = ['i32' for i in range(self.args_cnt)]

        header = f"define {self.rettype} @{self.name}({', '.join(arg_types)})" + "{\n" \
            if as_function else ""
        body = '\n'.join(statements)
        footer = "\n}" if as_function else ""

        return header + body + footer

    def add_code(self, code: LLVMCode):
        assert isinstance(code, LLVMCode)
        self.codes.append(code)


class Factor(object):
    def __init__(self, scope: Scope, name=None, val=None, size=0, ptr_offset=0):
        assert type(scope) is Scope
        self.scope = scope
        self.name = name
        self.val = val
        self.size = size
        self.ptr_offset = ptr_offset

    def __str__(self):
        if self.scope == Scope.GLOBAL:
            assert self.name is not None
            return f"@{self.name}"
        elif self.scope == Scope.LOCAL:
            assert self.val is not None, (self.scope, self.name, self.val, self.size, self.ptr_offset)
            return f"%{self.val}"
        elif self.scope == Scope.CONSTANT:
            assert self.val is not None
            return f"{self.val}"
        elif self.scope == Scope.FUNC:
            assert self.name is not None
            return f"@{self.name}"
        else:
            raise NotImplementedError()

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def vartype(self):
        return "i32" if self.size == 0 else f"[{self.size} x i32]"
    
    def replace(self, scope: Scope = None, name=None, val=None):
        scope = scope if scope is not None else self.scope
        name = name if name is not None else self.name
        val = val if val is not None else self.val
        print("scope", scope)
        return Factor(scope=scope, name=name, val=val)


def with_indent(s: str, level: int = 0) -> str:
    return f"{' ' * level}{s}"
