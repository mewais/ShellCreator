#!/usr/bin/python3

from pygments.lexer import RegexLexer
from pygments.token import *

class ShellLexer(RegexLexer):
    name = 'Shell'
    aliases = ['shell']
    filenames = ['*.shell']

    commands = 'if|while|elif|else|end'

    @classmethod
    def addCommand(cls, name):
        cls.commands += '|' + name
        cls.tokens = {
            'root': [
                (r'#.*', Comment.Single),
                (r'(?s)\$?"(\\.|[^"\\$])*"', String.Double),
                (r"(?s)\$'(\\\\|\\[0-7]+|\\.|[^'\\])*'", String.Single),
                (r"(?s)'.*?'", String.Single),
                (r'\$[a-zA-Z_]\w*', Name.Variable),
                (r'\d+(\.\d+)\b', Number),
                (r'\d+\b', Number),
                (r'\bTrue\b', Number),
                (r'\bFalse\b', Number),
                ('\\b(' + cls.commands + ')\\b', Keyword),
            ]
        }
