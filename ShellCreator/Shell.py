#!/usr/bin/python3

import logging
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer

from .Commands import *
from .Utils.ColoredLogs import ColorizedArgsFormatter

class Shell:
    def __init__(self, prompt, style=None, history='.shell.history'):
        self.prompt = prompt
        self.style = style
        self.history = history
        self.builtin_variables = {}
        self.variables = {}
        self.commands = {}
        self.commands['exit'] = Exit(self)
        self.commands['help'] = Help(self)
        self.commands['echo'] = Echo(self)
        self.commands['unset'] = Unset(self)
        self.commands['set'] = Set(self)
        self.commands['source'] = Source(self)

    def createLogging(self, formatter='SHELL %(levelname)s: %(message)s', enable_colors=True, verbosity='INFO'):
        self.logger = logging.getLogger('Shell')
        handler = logging.StreamHandler()
        if enable_colors:
            handler.setFormatter(ColorizedArgsFormatter(formatter))
        else:
            handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.setVerbosity(verbosity)

    def setVerbosity(self, verbosity='INFO'):
        if verbosity == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif verbosity == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif verbosity == 'WARNING':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == 'CRITICAL':
            self.logger.setLevel(logging.CRITICAL)

    def addCommand(name, cls):
        if name in self.commands:
            logger.critical('A command with the same name {} already exists', name)
            exit(7)
        if name is None or name == '':
            logger.critical('Please specify a valid name')
            exit(8)
        self.commands[name] = cls(self)

    def runScript(self, script, shell_after=True):
        # If script specified, open its file
        if script is not None:
            try:
                script = open(script, 'r')
                while True:
                    # Run the commands in it one by one
                    user_command = script.readline()
                    if not user_command:
                        script.close()
                        break
                    self.runCommand(user_command.strip('\n'))
            except IOError as e:
                self.logger.error('Could not open script. Caused by:\n\t{}', e)
        # If we come here, a script finished running, give a shell
        if shell_after:
            self.startPrompt()

    def startPrompt(self):
        while True:
            # Start the prompt, add styles in the same manner as prompt_toolkit
            user_command = prompt(self.prompt, style=self.style, history=FileHistory(self.history), lexer=PygmentsLexer(BashLexer))
            self.runCommand(user_command)

    def runCommand(self, user_command):
        # Ignore empty lines and comments
        if user_command == '' or user_command[0] == '#':
            return
        # Find the called command first
        user_command = user_command.split(' ', 1)
        command = user_command[0]
        if command in self.commands:
            # Run the command
            if len(user_command) == 2:
                self.commands[command].getArgs(user_command[1])
            elif len(user_command) == 1:
                self.commands[command].getArgs('')
            else:
                self.logger.critical('Failed to split command correctly')
                exit(2)
            self.commands[command].action()
        else:
            self.logger.error('Unknown command {}, run `help` to find all supported commands.', command)
        return
