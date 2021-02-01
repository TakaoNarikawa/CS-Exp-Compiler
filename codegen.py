from decls import Fundecl, Factor
from llvmcodes import LLVMCode, LLVMCodeWriteFormat, LLVMCodeReadFormat, LLVMCodeDeclarePrintf, LLVMCodeDeclareScanf
from typing import List


class CodeGenerator(object):
    def __init__(self) -> None:
        super().__init__()
        # グローバル変数を定義するための Fundecl を用意
        self.functions: List[Fundecl] = [Fundecl()]
        self.factorstack: List[Factor] = []

        self.write_enabled = False
        self.read_enabled = False

    @property
    def current_function(self):
        return self.functions[-1]

    @property
    def register(self):
        return self.current_function.register

    def add_function(self, name: str):
        self.functions.append(Fundecl(name))

    def pop_factor(self):
        return self.factorstack.pop()

    def push_factor(self, factor: Factor):
        self.factorstack.append(factor)

    def push_code(self, code: LLVMCode, func_idx=-1):
        self.functions[func_idx].codes.append(code)

    def export(self, filename, verbose=False):

        if self.write_enabled:
            self.push_code(LLVMCodeWriteFormat(), func_idx=0)
            self.push_code(LLVMCodeDeclarePrintf(), func_idx=0)
        
        if self.read_enabled:
            self.push_code(LLVMCodeReadFormat(), func_idx=0)
            self.push_code(LLVMCodeDeclareScanf(), func_idx=0)

        blocks = [f.to_string() for f in self.functions]
        content = '\n'.join(blocks)

        with open(filename, mode='w', encoding='utf-8') as f:
            f.write(content)

        if verbose:
            print(content)

    def enable_write(self):
        self.write_enabled = True
    def enable_read(self):
        self.read_enabled = True