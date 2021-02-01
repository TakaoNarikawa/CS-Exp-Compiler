# -*- coding: utf-8 -*-

from typing import List, Optional

from symtab import Scope
from llvmcodes import LLVMCode
import llvmcodes


class Fundecl(object):
    def __init__(self, name: Optional[str] = None, optimize_deadcode = False):
        self.name = name
        self.codes: List[LLVMCode] = []
        self.args_cnt = 0
        self.cntr = 1 # レジスタカウンター
        self.rettype = "i32"
        self.is_func = False
        self.optimize_deadcode_enabled = optimize_deadcode
        self.replace_register_dict = {}

    def register(self):
        t = self.cntr
        self.cntr += 1
        return t

    def to_string(self):
        if self.optimize_deadcode_enabled:
            self.optimize_deadcode()
        as_function = self.name is not None and len(self.name) > 0
        statements = [str(code) for code in self.codes]
        if as_function:
            statements = [with_indent(s, 2) for s in statements]

        arg_types = ['i32' for i in range(self.args_cnt)]

        header = f"define {self.rettype} @{self.name}({', '.join(arg_types)})" + "{\n" \
            if as_function else ""
        body = '\n'.join(statements)
        footer = "\n}" if as_function else ""

        # レジスタ番号の置き換え
        for rep_from, rep_to in sorted(self.replace_register_dict.items(), key=lambda x: x[0]):
            body = body.replace(f"%{rep_from}", f"%{rep_to}")

        return header + body + footer

    def optimize_deadcode(self):
        deps = []
        for code_index, code in enumerate(self.codes):
            print(code_index, code)
            if isinstance(code, llvmcodes.LLVMCodeAlloca):
                deps.append(Dependence(code_index, deps=[code.retval], required=True))
            if isinstance(code, llvmcodes.LLVMCodeGlobal):
                deps.append(Dependence(code_index, deps=[code.retval], required=True))
            if isinstance(code, llvmcodes.LLVMCodeStore):
                deps.append(Dependence(code_index, host=code.arg2, deps=[code.arg1]))
            if isinstance(code, llvmcodes.LLVMCodeLoad):
                deps.append(Dependence(code_index, host=code.arg1, deps=[code.arg2]))
            if isinstance(code, llvmcodes.LLVMCodeBrUncond):
                deps.append(Dependence(code_index, required=True, require_above=True))
            if isinstance(code, llvmcodes.LLVMCodeBrCond):
                deps.append(Dependence(code_index, deps=[code.arg1], required=True, require_above=True))
            if isinstance(code, llvmcodes.LLVMCodeIcmp):
                deps.append(Dependence(code_index, host=code.retval, deps=[code.arg1, code.arg2]))
            if isinstance(code, llvmcodes.LLVMCodeOperator):
                deps.append(Dependence(code_index, host=code.retval, deps=[code.arg1, code.arg2]))
            if isinstance(code, llvmcodes.LLVMCodeProcReturn):
                deps.append(Dependence(code_index, deps=[code.arg], required=True))
            if isinstance(code, llvmcodes.LLVMCodeWrite):
                deps.append(Dependence(code_index, host=code.retval, deps=[code.arg], required=True))
            if isinstance(code, llvmcodes.LLVMCodeRead):
                deps.append(Dependence(code_index, host=code.retval, deps=[code.arg], required=True))
            if isinstance(code, llvmcodes.LLVMCodeCallProc):
                deps.append(Dependence(code_index, host=code.retval, deps=code.args, required=True))
            if isinstance(code, llvmcodes.LLVMCodeGetPointer):
                deps.append(Dependence(code_index, host=code.arg1, deps=[code.arg2, code.index]))
        
        if not len(deps) > 0:
            return
        
        def search_host(host, start_i):
            for dep in deps[:start_i][::-1]:
                if dep.host == host:
                    return dep
            return None
        
        for i, dep in list(enumerate(deps))[::-1]:
            if dep.required:
                for d in dep.deps:
                    host = search_host(d, i)
                    if host is not None:
                        host.required = True
        
        require_above = False
        for i, dep in list(enumerate(deps))[::-1]:
            require_above = require_above or dep.require_above
            dep.required = dep.required or require_above
        
        print("=" * 5 + f"self.codesの依存関係 ({self.name})" + "=" * 5)
        for d in deps:
            print(d)
        
        print("↓ " * 5)

        required_deps = [d for d in deps if d.required]
        for d in required_deps:
            print(d)
            

        print(f"\n{len(deps)}行 -> {len(required_deps)}行へのコードの削減\n")

        # self.codes の中からいらないものを削除
        waste_deps = [d for d in deps if not d.required]
        waste_code_index = [d.code_index for d in waste_deps]
        self.codes = [c for i, c in enumerate(self.codes) if not i in waste_code_index]

        # レジスタ番号を連番に直す
        appear_registers = []
        for dep in required_deps:
            appear_registers += [dep.host] + dep.deps
        appear_registers = list(set([r for r in appear_registers if r is not None and type(r) is int]))

        for i, r in enumerate(appear_registers):
            if r < self.args_cnt:
                self.replace_register_dict[r] = r
            else:
                self.replace_register_dict[r] = i + 1
        print("self.replace_register_dict", self.replace_register_dict)

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
        return Factor(scope=scope, name=name, val=val)

class Dependence(object):
    def __init__(self, code_index: int, required=False, require_above=False, host: Optional[Factor] = None, deps: List[Factor] = []):
        self.code_index = code_index
        self.required = required
        self.require_above = require_above
        self.host = self.to_register(host)

        deps = [self.to_register(dep) for dep in deps]
        self.deps = [dep for dep in deps if dep is not None]

    def to_register(self, factor):
        if factor is None:
            return None
        if not isinstance(factor, Factor):
            return None
        if factor.scope == Scope.LOCAL:
            return factor.val
        if factor.scope == Scope.GLOBAL:
            return str(factor)
        return None

    def __str__(self):
        host = f"%{self.host}" if self.host is not None else "NULL"
        return f"{self.code_index+1}行目\t{host}\t-> ({self.deps}) \t | required: {self.required}"

    def __repr__(self) -> str:
        return self.__str__()


def with_indent(s: str, level: int = 0) -> str:
    return f"{' ' * level}{s}"

