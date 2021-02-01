# -*- coding: utf-8 -*-

from enum import Enum


class CmpType(Enum):
    EQ = 0   # eq (==)
    NE = 1      # ne (!=)
    SGT = 2     # sgt (>，符号付き)
    SGE = 3     # sge (>=，符号付き)
    SLT = 4     # slt (<，符号付き)
    SLE = 5     # sle (<=，符号付き)

    @classmethod
    def from_str(cls, v):
        if v == '=':
            return cls.EQ
        if v == '<>':
            return cls.NE
        if v == '>':
            return cls.SGT
        if v == '>=':
            return cls.SGE
        if v == '<':
            return cls.SLT
        if v == '<=':
            return cls.SLE
        raise ValueError(f'KeyError: {v}')

    def __str__(self) -> str:
        if self == CmpType.EQ:
            return 'eq'
        if self == CmpType.NE:
            return 'ne'
        if self == CmpType.SGT:
            return 'sgt'
        if self == CmpType.SGE:
            return 'sge'
        if self == CmpType.SLT:
            return 'slt'
        if self == CmpType.SLE:
            return 'sle'
        return super().__str__()


class LLVMCode(object):
    def __init__(self):
        pass

    def __str__(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.__str__()


class LLVMCodeAlloca(LLVMCode):
    '''
    %i = alloca i32, align 4
    現在実行中の関数のスタックフレーム上に int 型の変数を確保し，そのメモリ番地を返す
    '''

    def __init__(self, retval):
        super().__init__()
        self.retval = retval

    def __str__(self) -> str:
        return f"{self.retval} = alloca {self.retval.vartype}, align {16 if self.retval.size > 0 else 4}"


class LLVMCodeGlobal(LLVMCode):
    '''
    @n = common global i32 0, align 4
    i32 型の大域変数を確保し（0 で初期化），そのメモリ番地を返す．
    '''

    def __init__(self, retval):
        super().__init__()
        self.retval = retval

    def __str__(self) -> str:
        if self.retval.size > 0:
            return f"{self.retval} = common dso_local global [{self.retval.size} x i32] zeroinitializer, align 16"
        else:
            return f"{self.retval} = common global i32 0, align 4"


class LLVMCodeStore(LLVMCode):
    '''
    store i32 1234, i32* p, align 4
    i32 型の値 1234 を，p が指しているメモリ番地に格納している
    '''

    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self) -> str:
        return f"store i32 {self.arg1}, i32* {self.arg2}, align 4"


class LLVMCodeLoad(LLVMCode):
    '''
    r = load i32, i32* p, align 4
    メモリ p が指すメモリ番地から値を読み出し，レジスタ r に格納する
    '''

    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self) -> str:
        return f"{self.arg1} = load i32, i32* {self.arg2}, align 4"


class LLVMCodeBrUncond(LLVMCode):
    '''
    br label dest
    無条件でラベル dest へとジャンプする．
    '''

    def __init__(self, arg1):
        super().__init__()
        self.arg1 = arg1

    def __str__(self) -> str:
        return f"br label {self.arg1}"

class LLVMCodeBrCond(LLVMCode):
    '''
    br i1 %0 label %loop.end, label %loop.body
    条件付きでラベルへとジャンプする．
    '''

    def __init__(self, arg1, arg2, arg3):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __str__(self) -> str:
        return f"br i1 {self.arg1}, label {self.arg2}, label {self.arg3}"


class LLVMCodeIcmp(LLVMCode):
    '''
    r = icmp cond i32 op1, op2
    cond で指定された比較を行い，true/false の 2 値（型は i1）を返す．比較演算には以下の 10 種類がある．
    eq, ne, ugt, uge, ult, ule, sgt, sge, slt, sle
    '''

    def __init__(self, cmptype: CmpType, arg1, arg2, retval):
        super().__init__()
        self.cmptype = cmptype
        self.arg1 = arg1
        self.arg2 = arg2
        self.retval = retval

    def __str__(self) -> str:
        return f"{self.retval} = icmp {self.cmptype} i32 {self.arg1}, {self.arg2}"


class LLVMCodeOperator(LLVMCode):

    def __init__(self, arg1, arg2, retval, operator: str = ""):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self.retval = retval
        self.operator = operator

    def __str__(self) -> str:
        return f"{self.retval} = {self.operator} i32 {self.arg1}, {self.arg2}"


class LLVMCodeAdd(LLVMCodeOperator):
    '''
    %3 = add nsw i32 %2, 10
    '''

    def __init__(self, arg1: int, arg2: int, retval):
        super().__init__(arg1, arg2, retval, "add nsw")


class LLVMCodeSub(LLVMCodeOperator):
    '''
    %4 = sub nsw i32 100, %3
    '''

    def __init__(self, arg1: int, arg2: int, retval):
        super().__init__(arg1, arg2, retval, "sub nsw")


class LLVMCodeMul(LLVMCodeOperator):
    '''
    %5 = mul nsw i32 %4, 2
    '''

    def __init__(self, arg1: int, arg2: int, retval):
        super().__init__(arg1, arg2, retval, "mul nsw")


class LLVMCodeDiv(LLVMCodeOperator):
    '''
    %6 = sdiv i32 %5, %2
    '''

    def __init__(self, arg1: int, arg2: int, retval):
        super().__init__(arg1, arg2, retval, "sdiv")


class LLVMCodeProcReturn(LLVMCode):
    def __init__(self, arg = 0):
        self.arg = arg
    def __str__(self) -> str:
        return f"ret i32 {self.arg}"

class LLVMCodeRegisterLabel(LLVMCode):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def __str__(self) -> str:
        return f"{self.label}:"

class LLVMCodeWriteFormat(LLVMCode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return '@.str.write = private unnamed_addr constant [4 x i8] c"%d\\0A\\00", align 1'

class LLVMCodeReadFormat(LLVMCode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return '@.str.read = private unnamed_addr constant [3 x i8] c"%d\\00", align 1'

class LLVMCodeWrite(LLVMCode):
    def __init__(self, arg, retval):
        super().__init__()
        self.arg = arg
        self.retval = retval

    def __str__(self) -> str:
        return f'{self.retval} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.write, i64 0, i64 0), i32 {self.arg})'

class LLVMCodeRead(LLVMCode):
    def __init__(self, arg, retval):
        super().__init__()
        self.arg = arg
        self.retval = retval

    def __str__(self) -> str:
        return f'{self.retval} = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.read, i64 0, i64 0), i32* {self.arg})'

class LLVMCodeDeclarePrintf(LLVMCode):
    def __str__(self) -> str:
        return 'declare dso_local i32 @printf(i8*, ...) #1'

class LLVMCodeDeclareScanf(LLVMCode):
    def __str__(self) -> str:
        return 'declare dso_local i32 @__isoc99_scanf(i8*, ...) #1'

class LLVMCodeCallProc(LLVMCode):
    def __init__(self, func, args, retval):
        super().__init__()
        self.func = func
        self.args = args
        self.retval = retval

    def __str__(self) -> str:
        args = ', '.join([f"i32 {arg}" for arg in self.args])
        return f'{self.retval} = call i32 {self.func}({args})'

class LLVMCodeGetPointer(LLVMCode):
    def __init__(self, arg1, arg2, index, size):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self.index = index
        self.size = size

    def __str__(self) -> str:
        return f'{self.arg1} = getelementptr inbounds [{self.size} x i32], [{self.size} x i32]* {self.arg2}, i32 0, i32 {self.index}'