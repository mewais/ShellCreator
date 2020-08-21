#!/usr/bin/python3

import docopt
import logging
import pyparsing

from .Expressions import parseExpression, evaluateExpression

class Command:
    usage=''
    split=True
    logger=logging.getLogger('Shell')
    word_completer=None
    file_completer=None

    def __init__(self, shell):
        self.shell = shell

    def getArgs(self, command):
        self.args = None
        command_args = command
        if not self.split:
            command_args = [command_args]
        try:
            self.args = docopt.docopt(self.usage, argv=command_args)
        except docopt.DocoptExit:
            pass
        except SystemExit:
            pass
        except docopt.DocoptLanguageError:
            self.logger.critical('Documentation of command is not provided correctly.')
            exit(3)

    def action(self):
        raise NotImplementedError()

# Service Commands
class Exit(Command):
    usage='''
    exit

    Usage:
        exit [-h]

    Options:
        -h, --help                              Print this help message.
    '''

    def action(self):
        exit(0)

class Help(Command):
    word_completer = {'commands': None, 'variables': None, 'all': None}
    usage='''
    help

    Usage:
        help -h
        help commands
        help variables
        help all

    Options:
        -h, --help                              Print this help message.
    '''

    def action(self):
        if self.args is None:
            return
        if self.args['commands'] or self.args['all']:
            print('Commands: ')
            for command in self.shell.commands:
                print('\t- ' + command)
            print('Run `command-name -h` to get info about each command.')
        if self.args['variables'] or self.args['all']:
            print('Builtin Variables: ')
            for variable in self.shell.builtin_variables:
                print('\t- ' + variable)
            print('Variables: ')
            for variable in self.shell.variables:
                print('\t- ' + variable)
            print('Run `echo $var-name` to get the value of the variable.')

# Reading/Writing Variables
class Echo(Command):
    split=False
    usage='''
    echo

    Usage:
        echo -h
        echo EXPR

    Options:
        -h, --help                              Print this help message
    '''

    def action(self):
        if self.args is None:
            # Used the help flag
            return
        if self.args['EXPR'] is None:
            self.logger.error('Must specify an expression to echo.')
            return
        try:
            ast = parseExpression(self.args['EXPR'])
            value = evaluateExpression(ast, self.shell.builtin_variables, self.shell.variables)
            print(value)
        except NameError as e:
            # Already handled inside parseExpression
            pass
        except pyparsing.ParseException as e:
            self.logger.error('Couldn\'t parse expression {}.', self.args['EXPR'])

class Unset(Command):
    usage='''
    unset

    Usage:
        unset -h
        unset NAME

    Options:
        -h, --help                              Print this help message
    '''

    def action(self):
        if self.args is None:
            # Used the help flag
            return
        if self.args['NAME'] is None:
            self.logger.error('Must specify a variable to unset.')
            return
        if self.args['NAME'][0] != '$':
            self.logger.error('Variables must be prefixed with $.')
            return
        if self.args['NAME'][0] == '$' and self.args['NAME'][1] != '{':
            if self.args['NAME'][1:] in self.shell.builtin_variables:
                self.logger.error('Cannot unset builtin shell variables.')
                return
            if self.args['NAME'][1:] not in self.shell.variables:
                self.logger.error('Variable does not exist.')
                return
            del self.shell.variables[self.args['NAME'][1:]]
            self.shell.completer.deleteVariable(self.args['NAME'][1:])
        elif self.args['NAME'][0] == '$' and self.args['NAME'][1] == '{':
            if self.args['NAME'][-1] != '}':
                self.logger.error('Unbalanced curly brackets.')
                return
            if self.args['NAME'][2:-1] in self.shell.builtin_variables:
                self.logger.error('Cannot unset builtin shell variables.')
                return
            if self.args['NAME'][2:-1] not in self.shell.variables:
                self.logger.error('Variable does not exist.')
                return
            del self.shell.variables[self.args['NAME'][2:-1]]
            self.shell.completer.deleteVariable(self.args['NAME'][2:-1])

class Set(Command):
    split=False
    usage='''
    set

    Usage:
        set -h
        set EXPR

    Options:
        -h, --help                              Print this help message
    '''

    def action(self):
        if self.args is None:
            # Used the help flag
            return
        if self.args['EXPR'] is None:
            self.logger.error('Must specify an assignment to set.')
            return
        splits = self.args['EXPR'].split('=')
        if len(splits) != 2:
            self.logger.error('Invalid assignment.')
            return
        if splits[0] == '' or splits[1] == '':
            self.logger.error('Invalid assignment.')
            return
        try:
            ast = parseExpression(splits[1])
            value = evaluateExpression(ast, self.shell.builtin_variables, self.shell.variables)
            name = splits[0].replace(' ', '')
            if name in self.shell.builtin_variables:
                self.shell.builtin_variables[name] = value
            else:
                self.shell.variables[name] = value
                self.shell.completer.addVariable(name)
        except NameError as e:
            # Already handled inside parseExpression
            pass
        except pyparsing.ParseException as e:
            self.logger.error('Couldn\'t parse expression {}.', self.args['EXPR'])

class Source(Command):
    file_completer = ['sh', 'shell', 'script']
    split=False
    usage='''
    source

    Usage:
        source -h
        source FILE

    Options:
        -h, --help                              Print this help message
    '''

    def action(self):
        if self.args is None:
            # Used the help flag
            return
        if self.args['FILE'] is None:
            self.logger.error('Must specify a file to source.')
            return
        self.shell.runScript(self.args['FILE'], shell_after=False)
