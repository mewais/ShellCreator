#!/usr/bin/python3

from pygments.lexer import RegexLexer, include
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
                include('basic'),
                include('data'),
                include('interp'),
                include('math')
            ],
            'interp': [
                (r'\$\{#?', String.Interpol, 'curly'),
                (r'\$[a-zA-Z_]\w*', Name.Variable),  # user variable
                (r'\$(?:\d+|[#$?!_*@-])', Name.Variable),      # builtin
                (r'\$', Text)
            ],
            'basic': [
                ('\\b(' + cls.commands + ')\\b', Keyword),
                (r'#.*', Comment.Single),
                (r'\\[\w\W]', String.Escape)
            ],
            'data': [
                (r'(?s)\$?"(\\.|[^"\\$])*"', String.Double),
                (r'"', String.Double, 'string'),
                (r"(?s)\$'(\\\\|\\[0-7]+|\\.|[^'\\])*'", String.Single),
                (r"(?s)'.*?'", String.Single)
            ],
            'string': [
                (r'"', String.Double, '#pop'),
                (r'(?s)(\\\\|\\[0-7]+|\\.|[^"\\$])+', String.Double),
                include('interp')
            ],
            'curly': [
                (r'\}', String.Interpol, '#pop'),
                (r'\w+', Name.Variable),
                include('root')
            ],
            'math': [
                (r'\d+(\.\d+)\b', Number),
                (r'\d+\b', Number),
                (r'\bTrue\b', Number),
                (r'\bFalse\b', Number),
            ]
        }
