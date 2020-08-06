#!/usr/bin/python3

from ShellCreator.Shell import Shell
from ShellCreator.Commands import Command
from prompt_toolkit.styles import Style

# Styling shell
style = Style.from_dict({
    'program': '#0000aa',
    'separator': '#bbbb00'
})
prompt = [
    ('class:program', 'Example'),
    ('class:separator', '>>')
]

# Starting the shell
shell = Shell(prompt, style=style, history='prompt.history')
shell.createLogging()
shell.setVerbosity('DEBUG')

# Adding commands
class ReadFile(Command):
    usage='''
    read_file

    Usage:
        read_file -h
        read_file [--f FORMAT] FILE

    Options:
        -h, --help                    Print this help message
        -f FORMAT, --format=FORMAT    The format of the file to read
    '''

    def action(self):
        print(self.args)
shell.addCommand('read_file', ReadFile)

# Running
shell.startPrompt()
