#!/usr/bin/python3

import copy
import logging
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer

from .Commands import *
from .Highlighter import *
from .Expressions import parseExpression, evaluateExpression
from .Utils.ColoredLogs import ColorizedArgsFormatter

class Shell:
    def __init__(self, prompt, style=None, history='.shell.history'):
        self.prompt = prompt
        self.style = style
        self.history = history
        self.builtin_variables = {}
        self.variables = {}
        self.commands = {}
        self.addCommand('exit', Exit)
        self.addCommand('help', Help)
        self.addCommand('echo', Echo)
        self.addCommand('unset', Unset)
        self.addCommand('set', Set)
        self.addCommand('source', Source)
        self.inside_control = 0
        self.orig_prompt = []
        self.orig_style = []
        self.conditions = []
        self.condition_types = []
        self.condition_commands = []

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

    def addCommand(self, name, cls):
        if name in self.commands:
            logger.critical('A command with the same name {} already exists', name)
            exit(7)
        if name is None or name == '':
            logger.critical('Please specify a valid name')
            exit(8)
        self.commands[name] = cls(self)
        ShellLexer.addCommand(name)

    def addBuiltinVariable(self, name, value):
        if name in self.builtin_variables:
            logger.critical('A builtin variable with the same name exists')
            exit(11)
        self.builtin_variables[name] = value

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
            final_prompt = copy.deepcopy(self.prompt)
            if isinstance(self.prompt, str):
                final_prompt += ' '
            else:
                final_prompt.append((final_prompt[-1][0], ' '))
            # Start the prompt, add styles in the same manner as prompt_toolkit
            user_command = prompt(final_prompt, style=self.style, history=FileHistory(self.history), lexer=PygmentsLexer(ShellLexer))
            self.runCommand(user_command)

    def runCommand(self, entire_command):
        # Ignore empty lines and comments
        if entire_command == '' or entire_command[0] == '#':
            return
        # Find the called command first
        user_command = entire_command.split(' ', 1)
        command = user_command[0]
        if command == 'if' or command == 'while':
            # If the command is an if or a while, handle it
            self.inside_control += 1
            self.logger.debug('{} level: {}', command, self.inside_control)
            if self.inside_control == 1:
                # Change the prompt
                self.orig_prompt.append(self.prompt)
                self.orig_style.append(self.style)
                if isinstance(self.orig_prompt[-1], str):
                    self.prompt = '.' * len(self.orig_prompt[-1])
                else:
                    length = 0
                    for element in self.orig_prompt[-1]:
                        length += len(element[1])
                    self.prompt = '.' * length
                self.style = None
                # Create two lists to track commands inside each 
                # possible if. The first list contains the expressions
                # while the second is a list of lists containing 
                # the commands inside each if
                self.condition_types.append(command)
                self.conditions.append([user_command[1]])
                self.condition_commands.append([[]])
            else:
                # Or it is a control inside control, save, don't run
                self.condition_commands[-1][-1].append(entire_command)
        elif command == 'elif':
            self.logger.debug('{} level: {}', 'elif', self.inside_control)
            if self.inside_control == 1 and self.condition_types[-1] == 'if':
                # Add the new condition to the lists
                self.conditions[-1].append(user_command[1])
                self.condition_commands[-1].append([])
            elif self.inside_control > 1:
                # We're inside a parent control, just save
                self.condition_commands[-1][-1].append(entire_command)
            else:
                self.logger.error('elif without if')
        elif command == 'else':
            self.logger.debug('{} level: {}', 'else', self.inside_control)
            if self.inside_control == 1 and self.condition_types[-1] == 'if':
                # Add an empty place in the conditions list
                self.conditions[-1].append(None)
                self.condition_commands[-1].append([])
            elif self.inside_control > 1:
                # We're inside a parent control, just save
                self.condition_commands[-1][-1].append(entire_command)
            else:
                self.logger.error('else without if')
        elif entire_command.replace(' ', '') == 'end':
            self.logger.debug('{} level: {}', 'end', self.inside_control)
            self.inside_control -= 1
            if not self.inside_control:
                if self.condition_types[-1] == 'if':
                    # Check all conditions to find the correct one
                    index = len(self.conditions) - 1
                    for i, if_condition in enumerate(self.conditions[index]):
                        try:
                            if i == len(self.conditions[index]) - 1 and self.conditions[index][i] == None:
                                # If this is an else, and nothing before it is taken
                                value = True
                            else:
                                ast = parseExpression(if_condition)
                                value = evaluateExpression(ast, self.builtin_variables, self.variables)
                        except NameError as e:
                            break
                        except pyparsing.ParseException as e:
                            logger.error('Couldn\'t parse condition {}.', if_condition)
                            break
                        if value:
                            # Run the commands in those condition
                            for command in self.condition_commands[index][i]:
                                self.runCommand(command)
                            break
                elif self.condition_types[-1] == 'while':
                    # Make sure we have only one condition
                    if len(self.conditions[-1]) != 1 or len(self.condition_commands[-1]) != 1:
                        self.logger.fatal('Found while loop with more than one condition: {}, {}.', self.conditions[-1], self.condition_commands[-1])
                        exit(10)
                    # Check all conditions to find the correct one
                    index = len(self.conditions) - 1
                    while True:
                        try:
                            ast = parseExpression(self.conditions[index][0])
                            value = evaluateExpression(ast, self.builtin_variables, self.variables)
                        except NameError as e:
                            break
                        except pyparsing.ParseException as e:
                            logger.error('Couldn\'t parse condition {}.', self.conditions[index][0])
                            break
                        if value:
                            # Run the commands in those condition
                            for command in self.condition_commands[index][0]:
                                self.runCommand(command)
                        else:
                            break
                else:
                    self.logger.fatal('Recieved end for something other than if and while {}.', self.condition_types[-1])
                    exit(9)
                # Return prompt to normal
                self.prompt = self.orig_prompt[-1]
                self.style = self.orig_style[-1]
                del self.orig_prompt[-1]
                del self.orig_style[-1]
                del self.conditions[-1]
                del self.condition_types[-1]
                del self.condition_commands[-1]
            else:
                # Or it is an end inside control, save, don't run
                self.condition_commands[-1][-1].append(entire_command)
        elif command in self.commands:
            if self.inside_control:
                # Or it is a command inside if, save, don't run
                self.condition_commands[-1][-1].append(entire_command)
            else:
                # Otherwise it is a normal command
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
