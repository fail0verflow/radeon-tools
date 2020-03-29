#!/usr/bin/python3
import sys, pickle
import ply.lex as lex
import ply.yacc as yacc
from rai import *

states = (('mlcomment', 'exclusive'),)

literals = ['{','}','=',':',';','<','>',',']

tokens = [
    'COMMENT', 'CMTSTART', 'CMTEND', 'CMTBODY',

    'STRING',
    'INT',

    'SYMBOL',

    'NEWLINE',
]

reserved = (
    'SECTION_START',
    'SECTION_END',

    'CHIP_INFO',

    'CHIP_SPACES',
    'CHIP_SPACE',
    'BLOCK_INFO',
    'BLOCK_REGISTERS',
    'INDEX',
    'DATA',
    'NUM',
    'ALPHA',
    'R',
    'W',

    'FIXED',
)

tokens += reserved

# Read in an int.
def t_INT(t):
    r'-?(0x[0-9a-fA-F]+|(\d+))'
    t.value = int(t.value, 0)
    return t

def t_COMMENT(t):
    r'//[^\n]*'
    pass

def t_STRING(t):
    r'\"([^\\"]|(\\.))*\"'
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if c == "\n":
            t.lexer.lineno += 1
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str.replace("\r","") # bleh
    return t

def t_CMTSTART(t):
    r'/\*'
    t.lexer.begin('mlcomment')

def t_mlcomment_CMTBODY(t):
    r'([^*]|[*][^/])'
    t.lexer.lineno += len(t.value) - len(t.value.replace("\n",""))

def t_mlcomment_CMTEND(t):
    r'\*/'
    t.lexer.begin('INITIAL')

t_mlcomment_ignore = ''

# Track line numbers and newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if lexer.symbol_state == "force":
        lexer.symbol_state = "block"
    elif t.value in reserved:
        t.type = t.value
    return t

def t_lbrace(t):
     r'\{'
     t.type = '{'
     lexer.symbol_state = "force"
     return t

def t_rbrace(t):
     r'\}'
     t.type = '}'
     lexer.symbol_state = None
     return t

def t_semicolon(t):
     r';'
     t.type = ';'
     if lexer.symbol_state == "block":
        lexer.symbol_state = "force"
     return t

# Ignored characters
t_ignore = " \t\r"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

t_mlcomment_error = t_error

# Build the lexer
lexer = lex.lex()
lexer.symbol_state = None


# Parsing rules

########################## RAI ##########################

def p_rai(p):
    """rai : rai section
           |"""
    if len(p) == 1:
        p[0] = RAI()
    else:
        section = p[2]
        p[0] = rai = p[1]
        if isinstance(section, ChipInfo):
            rai.chip_info = section
        if isinstance(section, ChipSpaces):
            rai.chip_spaces = section
        if isinstance(section, Block):
            rai.blocks[section.info['BLOCK_NAME']] = section
            for k, v in section.registers.items():
                for space, addr in v.addrs:
                    if space not in rai.chip_spaces:
                        rai.chip_spaces[space] = ChipSpace()
                        rai.chip_spaces[space].addrs = {}
                    rai.chip_spaces[space].addrs[addr] = v

def p_section(p):
    """section : chip_info
               | chip_spaces
               | block"""
    p[0] = p[1]

########################## CHIP INFO ##########################

def p_chip_info(p):
    """chip_info : SECTION_START CHIP_INFO chip_info_body SECTION_END """
    p[0] = p[3]

def p_chip_info_body(p):
    """chip_info_body : chip_info_body basic_stmt
                      |"""
    if len(p) == 1:
        p[0] = ChipInfo()
    else:
        k, v = p[2]
        if k not in p[1]:
            p[1][k] = []
        p[1][k].append(v)
        p[0] = p[1]

########################## CHIP SPACES ##########################

def p_chip_spaces(p):
    """chip_spaces : SECTION_START CHIP_SPACES chip_spaces_body SECTION_END """
    p[0] = p[3]

def p_chip_spaces_body(p):
    """chip_spaces_body : chip_spaces_body chip_space
                        |"""
    if len(p) == 1:
        p[0] = ChipSpaces()
    else:
        k, v = p[2]
        p[1][k] = v
        p[0] = p[1]

def p_chip_space(p):
    """chip_space : CHIP_SPACE SYMBOL '{' chip_space_body '}' ';' """
    p[0] = (p[2], p[4])

def p_chip_space_body(p):
    """chip_space_body : chip_space_body basic_stmt
                       |"""
    if len(p) == 1:
        p[0] = ChipSpace()
        p[0].addrs = {}
    else:
        k, v = p[2]
        p[1][k] = v
        p[0] = p[1]

########################## BLOCK_INFO / BLOCK_REGISTERS ##########################

def p_block(p):
    """block : SECTION_START BLOCK_INFO block_info_body SECTION_END SECTION_START BLOCK_REGISTERS block_registers_body SECTION_END"""
    p[0] = Block()
    p[0].info = p[3]
    p[0].registers = p[7]

def p_block_info_body(p):
    """block_info_body : block_info_body basic_stmt
                      |"""
    if len(p) == 1:
        p[0] = dict()
    else:
        k, v = p[2]
        p[1][k] = v
        p[0] = p[1]

def p_block_registers_body(p):
    """block_registers_body : block_registers_body block_register
                            |"""
    if len(p) == 1:
        p[0] = dict()
    else:
        assert p[2].name not in p[1]
        p[1][p[2].name] = p[2]
        p[0] = p[1]

def p_block_register(p):
    """block_register : SYMBOL addrs INT reg_flags '{' reg_fields '}' ';'"""
    r = Register()
    r.name = p[1]
    r.addrs = p[2]
    r.width = p[3]
    r.flags = p[4]
    r.fields = p[6]
    p[0] = r

def p_reg_flags(p):
    """reg_flags : R
                 | W
                 |"""
    p[0] = p[1] if len(p) > 1 else None

def p_addrs(p):
    """addrs : addrs '<' SYMBOL ':' INT '>'
             |"""
    if len(p) == 1:
        p[0] = []
    else:
        p[1].append((p[3], p[5]))
        p[0] = p[1]

def p_reg_fields(p):
    """reg_fields : reg_fields reg_field
             |"""
    if len(p) == 1:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_reg_field(p):
    """reg_field : field_name INT ':' INT NUM field_flags ';'
                 | field_name INT ':' INT INDEX '=' SYMBOL field_flags ';'
                 | field_name INT ':' INT DATA '=' SYMBOL field_flags ';'
                 | field_name INT ':' INT ALPHA '{' alpha_defs '}' field_flags ';'
    """
    f = Field()
    f.name = p[1]
    f.hi = p[2]
    f.lo = p[4]
    f.type = p[5]
    if f.type in ('INDEX', 'DATA'):
        f.target = p[7]
        f.flags = p[8]
    elif f.type == 'ALPHA':
        f.values = p[7]
        f.flags = p[9]
    else:
        f.flags = p[6]
    p[0] = f

def p_field_name(p):
    """field_name : SYMBOL
                  | INDEX
                  | DATA"""
    p[0] = p[1]

def p_field_flags(p):
    """field_flags : R
                   | W
                   |"""
    p[0] = p[1] if len(p) > 1 else None

def p_alpha_defs(p):
    """alpha_defs : alpha_defs ',' alpha_def
                  | alpha_def"""
    if len(p) == 2:
        k, v = p[1]
        p[0] = {v: k}
    else:
        k, v = p[3]
        p[1][v] = k
        p[0] = p[1]

def p_alpha_def(p):
    """alpha_def : STRING '=' INT"""
    p[0] = (p[1], p[3])

########################## COMMON ##########################

def p_basic_stmt(p):
    """basic_stmt : SYMBOL '=' value ';'"""
    p[0] = (p[1], p[3])

def p_value(p):
    """value : INT
             | STRING
             | fixedbase
             | range
             | SYMBOL"""
    p[0] = p[1]

def p_range(p):
    """range : INT ':' INT"""
    p[0] = Range([p[1], p[3]])

def p_fixedbase(p):
    """fixedbase : FIXED INT"""
    p[0] = p[2]

def p_error(t):
    if t is None:
        print("Syntax error at EOF")
    else:
        print("Syntax error at %s:'%s' (line %d)" % (t.type,t.value,t.lineno))

parser = yacc.yacc(debug=1)

rai = parser.parse(open(sys.argv[1]).read())
with open(sys.argv[2], "wb") as fd:
    pickle.dump(rai, fd)
