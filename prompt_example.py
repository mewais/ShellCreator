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
    ('class:separator', '>> ')
]

# Starting the shell
shell = Shell(prompt, style=style, history='prompt.history')
shell.createLogging()
shell.setVerbosity('DEBUG')
shell.startPrompt()
