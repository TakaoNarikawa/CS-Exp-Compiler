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

        self.lbl_cnt = 0
        self.lbl_stack: List[int] = []

    @property
    def current_function(self):
        return self.functions[-1]

    def register(self):
        return self.current_function.register()

    def label_index(self):
        t = self.lbl_cnt
        self.lbl_cnt += 1
        self.lbl_stack.append(t)
        return t

    def add_function(self, name: str):
        self.functions.append(Fundecl(name))
    
    def move_to_last(self, name: str):
        found = [i for i, fn in enumerate(self.functions) if fn.name == name]
        if not len(found) > 0:
            raise RuntimeError(f'構文エラー: FORWARD 関数なし ... {name}')
        # 末端に持ってくる
        fn = self.functions.pop(found[0])
        self.functions.append(fn)

    def pop_factor(self):
        return self.factorstack.pop()

    def pop_all_factor(self):
        factors = self.factorstack[:]
        self.clear_factorstack()
        return factors

    def push_factor(self, factor: Factor):
        self.factorstack.append(factor)
    
    def clear_factorstack(self):
        self.factorstack = []

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

    def pop_label_stack(self, keep=False):
        if keep:
            return self.lbl_stack[-1]
        return self.lbl_stack.pop()
