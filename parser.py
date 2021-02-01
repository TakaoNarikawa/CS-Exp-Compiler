#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import ply.lex as lex
import ply.yacc as yacc
from symtab import SymbolTable, Scope
from decls import Fundecl, Factor
from codegen import CodeGenerator
import llvmcodes

symtab = SymbolTable()
codegen = CodeGenerator()
main_fundecl = Fundecl(name='main')

# トークンの定義
tokens = (
    'IDENT', 'NUMBER', 'BEGIN', 'DIV', 'DO', 'ELSE', 'END', 'FOR',
    'FORWARD', 'FUNCTION', 'IF', 'PROCEDURE', 'PROGRAM', 'READ', 'THEN', 'TO', 'VAR', 'WHILE', 'WRITE',
    'PLUS', 'MINUS', 'MULT', 'EQ', 'NEQ', 'LE', 'LT', 'GE', 'GT', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA',
    'SEMICOLON', 'COLON', 'INTERVAL', 'PERIOD', 'ASSIGN'
)

reserved = {
    'begin': 'BEGIN',
    'div': 'DIV',
    'do': 'DO',
    'else': 'ELSE',
    'end': 'END',
    'for': 'FOR',
    'forward': 'FORWARD',
    'function': 'FUNCTION',
    'if': 'IF',
    'procedure': 'PROCEDURE',
    'program': 'PROGRAM',
    'read': 'READ',
    'then': 'THEN',
    'to': 'TO',
    'var': 'VAR',
    'while': 'WHILE',
    'write': 'WRITE'
}

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_EQ = r'='
t_NEQ = r'<>'
t_LE = r'<='
t_LT = r'<'
t_GE = r'>='
t_GT = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r'\,'
t_SEMICOLON = r';'
t_COLON = r':'
t_INTERVAL = r'\.\.'
t_PERIOD = r'\.'
t_ASSIGN = r'\:='

t_ignore_COMMENT = r'\#.*'
t_ignore = ' \t'


def t_IDENT(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t


def t_NUMBER(t):
    r'[1-9][0-9]*|0'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Line %d: integer value %s is too large" % t.lineno, t.value)
        t.value = 0
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("不正な文字", t.value[0])
    t.lexer.skip(1)

#################################################################
# NOTE: 構文規則
#################################################################


def p_program(p):
    '''
    program : PROGRAM IDENT SEMICOLON outblock finalize_function PERIOD
    '''
    codegen.export("result.ll", verbose=True)


def p_outblock(p):
    '''
    outblock : var_decl_part subprog_decl_part link_main_function statement
    '''


def p_var_decl_part(p):
    '''
    var_decl_part : var_decl_list SEMICOLON
                  |
    '''
    if codegen.current_function.is_func:
        var = Factor(Scope.LOCAL, name=codegen.current_function.name, val=codegen.register())
        symtab.insert(var.name, scope=Scope.LOCAL, register=var.val)
        codegen.push_code(llvmcodes.LLVMCodeAlloca(var))


def p_var_decl_list(p):
    '''
    var_decl_list : var_decl_list SEMICOLON var_decl
                  | var_decl
    '''


def p_var_decl(p):
    '''
    var_decl : VAR id_list
    '''
    for var in codegen.pop_all_factor():
        if var.scope == Scope.GLOBAL:
            symtab.insert(var.name, scope=Scope.GLOBAL)
            codegen.push_code(llvmcodes.LLVMCodeGlobal(var), func_idx=0)
        if var.scope == Scope.LOCAL:
            symtab.insert(var.name, scope=Scope.LOCAL, register=var.val)
            codegen.push_code(llvmcodes.LLVMCodeAlloca(var))

def p_subprog_decl_part(p):
    '''
    subprog_decl_part : subprog_decl_list SEMICOLON
                      |
    '''


def p_subprog_decl_list(p):
    '''
    subprog_decl_list : subprog_decl_list SEMICOLON subprog_decl
                      | subprog_decl
    '''


def p_subprog_decl(p):
    '''
    subprog_decl : proc_decl
                 | func_decl
    '''


def p_proc_decl(p):
    '''
    proc_decl : PROCEDURE proc_name closure
    '''

def p_func_decl(p):
    '''
    func_decl : FUNCTION func_name closure
    '''

def p_proc_name(p):
    '''
    proc_name : IDENT link_proc
    '''

def p_func_name(p):
    '''
    func_name : IDENT link_proc
    '''
    codegen.current_function.is_func = True


def p_closure(p):
    '''
    closure : SEMICOLON enter_block inblock leave_block finalize_function remove_local_var
            | LPAREN enter_block id_list link_args RPAREN SEMICOLON inblock leave_block finalize_function remove_local_var
    '''


def p_inblock(p):
    '''
    inblock :  var_decl_part statement
    '''


def p_statement_list(p):
    '''
    statement_list : statement_list SEMICOLON statement
                   | statement
    '''
    codegen.clear_factorstack()

def p_statement(p):
    '''
    statement : assignment_statement
              | if_statement
              | while_statement
              | for_statement
              | proc_call_statement
              | null_statement
              | block_statement
              | read_statement
              | write_statement
    '''


def p_assignment_statement(p):
    '''
    assignment_statement : IDENT ASSIGN expression lookup_id
    '''
    ident = p[1]

    arg1 = codegen.pop_factor()
    arg2 = parse_variable(ident)

    codegen.push_code(llvmcodes.LLVMCodeStore(arg1, arg2))


def p_if_statement(p):
    '''
    if_statement : IF condition if_condition THEN statement if_else else_statement if_end
    '''




def p_else_statement(p):
    '''
    else_statement : ELSE statement
                   |
    '''


def p_while_statement(p):
    '''
    while_statement : WHILE while_init condition while_condition DO statement while_end
    '''



def p_for_statement(p):
    '''
    for_statement : FOR IDENT lookup_id ASSIGN expression TO expression for_init DO statement for_end
    '''


def p_proc_call_statement(p):
    '''
    proc_call_statement : proc_call_name proc_call
                        | proc_call_name LPAREN arg_list RPAREN proc_call
    '''

def p_proc_call_name(p):
    '''
    proc_call_name : IDENT
    '''
    ident = p[1]
    scope = symtab.lookup(ident, [Scope.FUNC]).scope

    arg = Factor(scope, name=ident)
    codegen.push_factor(arg)

def p_block_statement(p):
    '''
    block_statement : BEGIN statement_list END
    '''


def p_read_statement(p):
    '''
    read_statement : READ LPAREN IDENT lookup_id RPAREN
    '''
    ident = p[3]
    scope = symtab.lookup(ident).scope
    val = Factor(scope, name=ident)

    # read_value_addr: i32* read で読み取った内容を持つアメモリ番地
    read_value_addr = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeAlloca(read_value_addr))
    retval = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeRead(read_value_addr, retval))

    # read_value_addr -> read_value
    read_value = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeLoad(read_value, read_value_addr))

    codegen.push_code(llvmcodes.LLVMCodeStore(read_value, val))
    codegen.enable_read()

def p_write_statement(p):
    '''
    write_statement : WRITE LPAREN expression RPAREN
    '''

    arg = codegen.pop_factor()
    retval = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeWrite(arg, retval))
    codegen.enable_write()


def p_null_statement(p):
    '''
    null_statement :
    '''


def p_condition(p):
    '''
    condition : expression EQ expression
              | expression NEQ expression
              | expression LT expression
              | expression LE expression
              | expression GT expression
              | expression GE expression
    '''
    arg2 = codegen.pop_factor()
    arg1 = codegen.pop_factor()
    retval = Factor(Scope.LOCAL, val=codegen.register())
    ope = llvmcodes.CmpType.from_str(p[2])

    codegen.push_code(llvmcodes.LLVMCodeIcmp(ope, arg1, arg2, retval))
    codegen.push_factor(retval)


def p_expression(p):
    '''
    expression : term
               | PLUS term
               | MINUS term
               | expression PLUS term
               | expression MINUS term
    '''

    if len(p) < 3: 
        return

    if len(p) == 3:
        arg2 = codegen.pop_factor()
        arg1 = Factor(Scope.CONSTANT, val=0)
    else:
        arg2 = codegen.pop_factor()
        arg1 = codegen.pop_factor()

    retval = Factor(Scope.LOCAL, val=codegen.register())

    operator = p[2]
    assert operator == '+' or operator == '-'

    LLVMCodeClass = llvmcodes.LLVMCodeAdd \
        if operator == '+' else llvmcodes.LLVMCodeSub

    l = LLVMCodeClass(arg1, arg2, retval)

    codegen.push_code(l)
    codegen.push_factor(retval)


def p_term(p):
    '''
    term : factor
         | term MULT factor
         | term DIV factor
    '''
    if len(p) < 3:
        return

    arg2 = codegen.pop_factor()
    arg1 = codegen.pop_factor()
    retval = Factor(Scope.LOCAL, val=codegen.register())

    LLVMCodeClass = llvmcodes.LLVMCodeMul \
        if p[2] == '*' else llvmcodes.LLVMCodeDiv
    l = LLVMCodeClass(arg1, arg2, retval)

    codegen.push_code(l)
    codegen.push_factor(retval)


def p_factor(p):
    '''
    factor : var_name
           | proc_call_name LPAREN arg_list RPAREN proc_call
           | NUMBER
           | LPAREN expression RPAREN
    '''
    if len(p) != 2:
        return
        
    if p[1] is not None:
        val = Factor(Scope.CONSTANT, val=p[1])
        codegen.push_factor(val)
    else:
        var = codegen.pop_factor()
        retval = Factor(Scope.LOCAL, val=codegen.register())
        l = llvmcodes.LLVMCodeLoad(retval, var)
        codegen.push_code(l)
        codegen.push_factor(retval)


def p_var_name(p):
    '''
    var_name : IDENT lookup_id
    '''
    ident = p[1]
    var = parse_variable(ident)
    codegen.push_factor(var)


def p_arg_list(p):
    '''
    arg_list : expression
             | arg_list COMMA expression
    '''

def p_id_list(p):
    '''
    id_list : IDENT link_id
            | id_list COMMA IDENT link_id
    '''

#################################################################
# NOTE: SymbolTable用
#################################################################


def p_link_proc(p):
    '''
    link_proc :
    '''
    symtab.insert(latest_id_name(p), 'proc')
    codegen.add_function(latest_id_name(p))


def p_lookup_id(p):
    '''
    lookup_id :
    '''
    symtab.lookup(latest_id_name(p))

def p_enter_block(p):
    '''
    enter_block :
    '''
    symtab.increase_depth()

def p_leave_block(p):
    '''
    leave_block :
    '''
    symtab.decrease_depth()

def p_link_id(p):
    '''
    link_id :
    '''
    ident = latest_id_name(p)
    scope = symtab.scope()

    assert scope == Scope.GLOBAL or scope == Scope.LOCAL

    if scope == Scope.GLOBAL:
        val = Factor(scope, name=ident)

    if scope == Scope.LOCAL:
        val = Factor(scope, name=ident, val=codegen.register())

    codegen.push_factor(val)

def p_link_args(p):
    '''
    link_args :
    '''
    args = codegen.pop_all_factor()
    codegen.current_function.args_cnt = len(args)
    
    for arg in args:
        arg_var = Factor(scope=Scope.LOCAL, val=codegen.register())
        symtab.insert(arg.name, scope=Scope.LOCAL, register=arg_var.val)
        codegen.push_code(llvmcodes.LLVMCodeAlloca(arg_var))
        codegen.push_code(llvmcodes.LLVMCodeStore(arg.replace(val=arg.val - 1), arg_var))
        
    # 記号表の関数の引数の数を更新する
    func = symtab.lookup(codegen.current_function.name, [Scope.FUNC])
    symtab.update_args_cnt(func, cnt=len(args))


def p_remove_local_var(p):
    '''
    remove_local_var :
    '''
    symtab.remove_local_var()

def p_proc_call(p):
    '''
    proc_call :
    '''

    factors = codegen.pop_all_factor()
    func = factors[0]
    args = factors[1:]

    # 引数に対応した関数があるかチェック
    symtab.lookup(func.name, [Scope.FUNC], args_cnt = len(args))
    print(symtab.symbols)

    retval = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeCallProc(func, args, retval))
    codegen.push_factor(retval)

#################################################################
# NOTE: コード生成用
#################################################################


def p_link_main_function(p):
    '''
    link_main_function :
    '''
    codegen.add_function("main")

def p_finalize_function(p):
    '''
    finalize_function :
    '''
    if not codegen.current_function.is_func:
        codegen.push_code(llvmcodes.LLVMCodeProcReturn())
    else:
        var = parse_variable(codegen.current_function.name)
        retval = Factor(Scope.LOCAL, val=codegen.register())
        codegen.push_code(llvmcodes.LLVMCodeLoad(retval, var))
        codegen.push_code(llvmcodes.LLVMCodeProcReturn(retval))

# NOTE: WHILE

def p_while_init(p):
    '''
    while_init :
    '''
    l_init = Factor(Scope.LOCAL, val="while.init")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l_init))
    # 行き先 while.init を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("while.init"))

def p_while_condition(p):
    '''
    while_condition :
    '''

    # 条件分岐の行き先を決定
    cond = codegen.pop_factor()
    l1 = Factor(Scope.LOCAL, val="while.body")
    l2 = Factor(Scope.LOCAL, val="while.end")

    codegen.push_code(llvmcodes.LLVMCodeBrCond(cond, l1, l2))

    # 行き先 while.body ( statement の部分 ) を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("while.body"))

def p_while_end(p):
    '''
    while_end :
    '''

    # while.init に戻る
    l1 = Factor(Scope.LOCAL, val="while.init")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l1))

    # 行き先 while.end を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("while.end"))

# NOTE: IF - ELSE

def p_if_condition(p):
    '''
    if_condition :
    '''
    # 条件分岐の行き先を決定
    cond = codegen.pop_factor()
    l1 = Factor(Scope.LOCAL, val="if.true")
    l2 = Factor(Scope.LOCAL, val="if.else")

    codegen.push_code(llvmcodes.LLVMCodeBrCond(cond, l1, l2))

    # 行き先 if.true を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("if.true"))

def p_if_else(p):
    '''
    if_else :
    '''

    l1 = Factor(Scope.LOCAL, val="if.end")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l1))

    # 行き先 if.else を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("if.else"))

def p_if_end(p):
    '''
    if_end :
    '''

    l1 = Factor(Scope.LOCAL, val="if.end")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l1))

    # 行き先 if.end を作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("if.end"))

# NOTE: FOR 

def p_for_init(p):
    '''
    for_init :
    '''

    # for n:= 2 to 100
    # ↓
    # for ident := range_from to range_to

    ident = latest_id_name(p)
    
    range_to = codegen.pop_factor()
    range_from = codegen.pop_factor()
    var = parse_variable(ident)

    # n := 2
    codegen.push_code(llvmcodes.LLVMCodeStore(range_from, var))
    
    # 初期化時は無条件で statement に移動
    l_body = Factor(Scope.LOCAL, val="for.body")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l_body))

    # statement が終わったあとに戻ってくる for.condition のポイントを作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("for.condition"))

    # n++ 
    ## n をレジスタに読み込み
    reg_ident = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeLoad(reg_ident, var))
    ## n + 1
    one = Factor(Scope.CONSTANT, val=1)
    reg_ident_increased = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeAdd(reg_ident, one, reg_ident_increased))
    ## レジスタの内容を n に戻す
    codegen.push_code(llvmcodes.LLVMCodeStore(reg_ident_increased, var))

    # n が range_from に到達したかのチェック
    ## n < range_to
    cond = Factor(Scope.LOCAL, val=codegen.register())
    codegen.push_code(llvmcodes.LLVMCodeIcmp(llvmcodes.CmpType.SLT, reg_ident_increased, range_to, cond))

    l_end = Factor(Scope.LOCAL, val="for.end")
    codegen.push_code(llvmcodes.LLVMCodeBrCond(cond, l_body, l_end))

    # for.body の作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("for.body"))

def p_for_end(p):
    '''
    for_end :
    '''
    # statement 終了後は強制的に for.condition に戻して n < range_to を評価する
    l_cond = Factor(Scope.LOCAL, val="for.condition")
    codegen.push_code(llvmcodes.LLVMCodeBrUncond(l_cond))

    # for.end の作成
    codegen.push_code(llvmcodes.LLVMCodeRegisterLabel("for.end"))


#################################################################
# NOTE: その他関数
#################################################################


def latest_id_name(p):
    ids = [t for t in p.stack if t.type == 'IDENT']
    if not len(ids) > 0:
        print('IDENTが見つかりませんでした')
        exit()
    return ids[-1].value

def parse_variable(v):
    symbol = symtab.lookup(v)
    scope = symbol.scope

    if scope == Scope.GLOBAL:
        return Factor(scope, name=v)
    if scope == Scope.LOCAL:
        return Factor(scope, val=symbol.register)
    
    raise ValueError()


#################################################################
# NOTE: 構文解析エラー時の処理
#################################################################

def p_error(p):
    if p:
        print(f'{p.lineno} 行目: 構文エラー 予期しない文字 "{p.value}" (type: {p.type})')


if __name__ == "__main__":
    lexer = lex.lex(debug=0)  # 字句解析器
    yacc.yacc()  # 構文解析器

    # ファイルを開いて
    data = open(sys.argv[1]).read()
    # 解析を実行
    
    try:
        yacc.parse(data, lexer=lexer)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("\n\n--- log --- \n\n")
        codegen.export("error.ll", verbose=True)