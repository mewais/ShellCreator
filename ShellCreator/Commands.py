#!/usr/bin/python3

import docopt
import logging
import pyparsing

from .Variables import variables, parseEquation, evaluateEquation

logger = logging.getLogger('Shell')
commands = {}

class Command:
    usage=''
    split=True
    args=None

    @classmethod
    def getArgs(cls, command):
        command_args = command
        if not cls.split:
            command_args = [command_args]
        try:
            cls.args = docopt.docopt(cls.usage, argv=command_args)
        except docopt.DocoptExit:
            pass
        except SystemExit:
            pass
        except docopt.DocoptLanguageError:
            logger.critical('Documentation of command is not provided correctly.')
            exit(3)

    @classmethod
    def action(cls):
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

    @classmethod
    def action(cls):
        exit(0)
commands['exit'] = Exit

class Help(Command):
    usage='''
    help

    Usage:
        help --commands
        help --variables
        help --commands --variables

    Options:
        -h, --help                              Print this help message.
        -c, --commands                          List all commands.
        -v, --variables                         List all variables.
    '''

    @classmethod
    def action(cls):
        if cls.args is None:
            cls.args = {'--commands': True, '--variables': False}
        if cls.args['--commands'] is not None:
            print('Commands: ')
            for command in commands:
                print('\t- ' + command)
            print('Run `command-name -h` to get info about each command.')
        if cls.args['--variables'] is not None:
            print('Variables: ')
            for variable in variables:
                print('\t- ' + variable)
            print('Run `echo $var-name` to get the value of the variable.')
commands['help'] = Help

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

    @classmethod
    def action(cls):
        if cls.args is None:
            # Used the help flag
            return
        if cls.args['EXPR'] is None:
            logger.error('Must specify an expression to echo.')
            return
        try:
            ast = parseEquation(cls.args['EXPR'])
            value = evaluateEquation(ast)
            print(value)
        except NameError as e:
            # Already handled inside parseEquation
            pass
commands['echo'] = Echo

class Unset(Command):
    usage='''
    unset

    Usage:
        unset -h
        unset NAME

    Options:
        -h, --help                              Print this help message
    '''

    @classmethod
    def action(cls):
        if cls.args is None:
            # Used the help flag
            return
        if cls.args['NAME'] is None:
            logger.error('Must specify a variable to unset.')
            return
        if cls.args['NAME'][0] != '$':
            logger.error('Variables must be prefixed with $.')
            return
        if cls.args['NAME'][1:] not in variables:
            logger.error('Variable does not exist.')
            return
        del variables[cls.args['NAME'][1:]]
commands['unset'] = Unset

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

    @classmethod
    def action(cls):
        if cls.args is None:
            # Used the help flag
            return
        if cls.args['EXPR'] is None:
            logger.error('Must specify an assignment to set.')
            return
        splits = cls.args['EXPR'].split('=')
        if len(splits) != 2:
            logger.error('Invalid assignment')
            return
        if splits[0] == '' or splits[1] == '':
            logger.error('Invalid assignment')
            return
        try:
            ast = parseEquation(splits[1])
            value = evaluateEquation(ast)
            variables[splits[0]] = value
        except NameError as e:
            # Already handled inside parseEquation
            pass
commands['set'] = Set

def addCommand(name, cls):
    if name in commands:
        logger.critical('A command with the same name {} already exists', name)
        exit(7)
    if name is None or name == '':
        logger.critical('Please specify a valid name')
        exit(8)
    commands[name] = cls
