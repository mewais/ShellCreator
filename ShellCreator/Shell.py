#!/usr/bin/python3

import logging
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer

from Commands import commands, Command
from Utils.ColoredLogs import ColorizedArgsFormatter

class Shell:
    def createLogging(self, formatter='SHELL %(levelname)s: %(message)s', enable_colors=True):
        self.logger = logging.getLogger('Shell')
        handler = logging.StreamHandler()
        if enable_colors:
            handler.setFormatter(ColorizedArgsFormatter(formatter))
        else:
            handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

    def runScript(self, script, prompt, style=None, history='.shell.history'):
        while True:
            # If script specified, open its file
            if script is not None:
                try:
                    self.script = open(script, 'r')
                except Exception as e:
                    logger.error('Could not open script. Caused by:\n\t{}', e)
                    exit(1)
            # Run the commands in it one by one
            user_command = script.readline()
            if not user_command:
                script.close()
                break
            runCommand(user_command)
        # If we come here, a script finished running, give a shell
        startPrompt(prompt, style, history)

    def startPrompt(prompt, style=None, history='.shell.history'):
        while True:
            # Start the prompt, add styles in the same manner as prompt_toolkit
            user_command = prompt(prompt, style=style, history=FileHistory(history), lexer=PygmentsLexer(BashLexer))
            runCommand(user_command)

    def runCommand(user_command):
        # Ignore empty lines and comments
        if user_command == '' or user_command[0] == '#':
            return
        # Find the called command first
        user_command = user_command.split(' ', 1)
        command = user_command[0]
        if command in commands:
            # Run the command
            if len(user_command) == 2:
                commands[command].getArgs(user_command[1])
            elif len(user_command) == 1:
                commands[command].getArgs('')
            else:
                logger.critical('Failed to split command correctly')
                exit(2)
            commands[command].action()
        else:
            logger.error('Unknown command, run `help` to find all supported commands.')
        return
