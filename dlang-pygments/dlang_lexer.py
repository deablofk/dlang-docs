"""Pygments lexer for the DLang systems programming language (working name)."""
from pygments.lexer import RegexLexer, words, include
from pygments.token import (Comment, Keyword, Name, String, Number, Operator,
                            Punctuation, Whitespace)

__all__ = ['DLangLexer']


class DLangLexer(RegexLexer):
    name = 'DLang'
    aliases = ['dlang']
    filenames = ['*.dlang']
    url = 'https://example.invalid/dlang'

    keywords = (
        'val', 'var', 'const', 'if', 'else', 'match', 'while', 'for',
        'return', 'defer', 'try', 'catch', 'throws', 'import', 'inline',
        'namespace', 'struct', 'enum', 'interface', 'as', 'lazy', 'ref',
        'break', 'continue', 'in', 'quote', 'nocopy',
        # parameter conventions
        'borrow', 'inout', 'sink', 'set', 'sending',
        # structured concurrency (contextual keywords)
        'spawn', 'await',
        'operator_add', 'operator_get', 'operator_set',
    )
    builtin_types = (
        'byte', 'short', 'int', 'long', 'float', 'double', 'boolean',
        'char', 'string', 'String', 'any', 'type', 'void',
        'Ptr', 'List', 'Map', 'Allocator', 'ByteBuf', 'Pool',
        # concurrency (std/concurrency)
        'Thread', 'Task', 'Mutex', 'Channel', 'Shared', 'Atomic',
        'ChanItem', 'Selected', 'SelectSet',
        'Iter', 'Buffer',
    )
    builtins = (
        'println', 'print', 'cast', 'funcaddr',
    )
    constants = ('true', 'false', 'null')

    tokens = {
        'root': [
            (r'\s+', Whitespace),
            (r'//.*?$', Comment.Single),
            (r'/\*', Comment.Multiline, 'comment'),
            # annotations: @intrinsic, @comptime, @macro, @reflete ...
            (r'@[a-zA-Z_]\w*', Name.Decorator),
            # compile-time directives: #rodar, #se, #assert, #<macro> ...
            (r'#[a-zA-Z_]\w*', Name.Decorator),
            # triple-quoted text blocks
            (r'"""', String, 'tstring'),
            (r'"', String, 'string'),
            (r'\b\d+\.\d+\b', Number.Float),
            (r'\b0[xX][0-9a-fA-F_]+\b', Number.Hex),
            (r'\b0[bB][01_]+\b', Number.Bin),
            (r'\b0[oO][0-7_]+\b', Number.Oct),
            (r'\b\d[\d_]*\b', Number.Integer),
            (words(constants, suffix=r'\b'), Keyword.Constant),
            # the universal placeholder '_' (standalone)
            (r'_\b', Name.Builtin.Pseudo),
            # pseudo/allocator-style builtins: _alloc, _gcAlloc, _exec ...
            (r'_[a-zA-Z]\w*', Name.Builtin.Pseudo),
            (words(keywords, suffix=r'\b'), Keyword),
            (words(builtin_types, suffix=r'\b'), Keyword.Type),
            (words(builtins, suffix=r'\b'), Name.Builtin),
            # range operator (before generic operators)
            (r'\.\.', Operator),
            # the :: definition / compile-time binding operator
            (r'::', Operator),
            (r'->', Operator),
            (r'[+\-*/%=<>!&|\^~@]+', Operator),
            (r'[.,;:(){}\[\]]', Punctuation),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'comment': [
            (r'[^*/]+', Comment.Multiline),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        'string': [
            (r'\$\{', String.Interpol, 'interp'),
            (r'\\.', String.Escape),
            (r'"', String, '#pop'),
            (r'[^"\\$]+', String),
            (r'\$', String),
        ],
        'tstring': [
            (r'\$\{', String.Interpol, 'interp'),
            (r'\\.', String.Escape),
            (r'"""', String, '#pop'),
            (r'[^"\\$]+', String),
            (r'"', String),
            (r'\$', String),
        ],
        # ${ ... } interpolation: highlight the inner expression like code
        'interp': [
            (r'\}', String.Interpol, '#pop'),
            include('root'),
        ],
    }
