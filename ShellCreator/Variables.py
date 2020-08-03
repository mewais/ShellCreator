#!/usr/bin/python3

import pyparsing
import logging
import operator

from .Utils.StringUtils import stringToNumber
from .Utils.Operators import operator_and, operator_or

logger = logging.getLogger('Shell')
builtin_variables = {}
variables = {}

variable_names = pyparsing.Combine(pyparsing.Literal('$') + pyparsing.Word(pyparsing.alphanums + '_'))
integer = pyparsing.Word(pyparsing.nums)
double = pyparsing.Combine(pyparsing.Word(pyparsing.nums) + '.' + pyparsing.Word(pyparsing.nums))
parser = pyparsing.operatorPrecedence(variable_names | double | integer, [
                                ('**', 2, pyparsing.opAssoc.RIGHT),
                                ('-', 1, pyparsing.opAssoc.RIGHT),
                                ('*', 2, pyparsing.opAssoc.LEFT),
                                ('/', 2, pyparsing.opAssoc.LEFT),
                                ('//', 2, pyparsing.opAssoc.LEFT),
                                ('%', 2, pyparsing.opAssoc.LEFT),
                                ('+', 2, pyparsing.opAssoc.LEFT),
                                ('-', 2, pyparsing.opAssoc.LEFT),
                                ('>', 2, pyparsing.opAssoc.LEFT),
                                ('>=', 2, pyparsing.opAssoc.LEFT),
                                ('<', 2, pyparsing.opAssoc.LEFT),
                                ('<=', 2, pyparsing.opAssoc.LEFT),
                                ('==', 2, pyparsing.opAssoc.LEFT),
                                ('!=', 2, pyparsing.opAssoc.LEFT),
                                ('not', 1, pyparsing.opAssoc.RIGHT),
                                ('and', 2, pyparsing.opAssoc.LEFT),
                                ('or', 2, pyparsing.opAssoc.LEFT)])
unary_operators = {
    '-': operator.neg,
    'not': operator.not_,
}
right_binary_operators = {
    '**': operator.add
}
left_binary_operators = {
    '*': operator.mul,
    '/': operator.truediv,
    '//': operator.floordiv,
    '%': operator.mod,
    '+': operator.add,
    '-': operator.sub,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    'and': operator_and,
    'or': operator_or,
}


def buildAST(function):
    # Build an AST and remove redundant paranthesis, etc.
    ast = {}
    if isinstance(function, str):
        # Just a literal
        return function
    elif isinstance(function, list) and len(function) == 2:
        # There is only one unary operator, which is NOT or NEG
        child_ast = buildAST(function[1])
        ast[function[0]] = child_ast
    elif isinstance(function, list):
        # There is only one top level operator, with 2 or more inputs
        ast[function[1]] = []
        for i in range(0, len(function), 2):
            child_ast = buildAST(function[i])
            key = next(iter(child_ast))     # Key of child dict
            if key == function[1]:
                # flatten, if the child is the same operand as us
                ast[function[1]].extend(child_ast[key])
            else:
                ast[function[1]].append(child_ast)
    else:
        logger.critical('Unknown type {} encountered while building AST.', type(function))
        exit(4)
    if len(ast) > 1:
        logger.critical('AST must have only one key.')
        exit(5)
    return ast

def printAST(ast, prefix='', child_prefix=''):
    if isinstance(ast, str) or isinstance(ast, int) or isinstance(ast, float):
        # This should only happen on the top level
        if prefix != '' or child_prefix != '':
            logger.critical('Unexpected string in the AST.')
            exit(6)
        logger.debug(ast)
        return

    if not isinstance(ast, dict):
        logger.critical('Expecting AST as a dictionary, got {} instead.', ast)
        exit(7)

    # Get the only key
    key = next(iter(ast))

    # Print node head
    logger.debug(prefix + '{}', key)
    # Print children
    if isinstance(ast[key], list):
        for i, element in enumerate(ast[key]):
            if isinstance(element, dict):
                if i == len(ast[key]) - 1:
                    printAST(element, child_prefix + '|__', child_prefix + '   ')
                else:
                    printAST(element, child_prefix + '|__', child_prefix + '|  ')
            else:
                logger.debug(child_prefix + '|__{}', element)
    elif isinstance(ast[key], str):
        logger.debug(child_prefix + '|__{}', ast[key])
    elif isinstance(ast[key], dict):
        printAST(ast[key], child_prefix + '|__', child_prefix + '   ')
    else:
        logger.critical('AST includes an unknown type. Got {}.', ast[key])
        exit(8)

def substituteAST(ast):
    if isinstance(ast, str):
        # This should only happen on the top level
        if ast[0] == '$':
            if ast[1:] in variables:
                ast = variables[ast[1:]]
            else:
                logger.error('Variable {} does not exist.', ast[1:])
                raise NameError('Variable does not exist')
        else:
            try:
                ast = stringToNumber(ast)
            except ValueError as e:
                logger.critical('All strings must be variables or number literals. Got {}', ast)
                exit(9)
        return ast
    
    if not isinstance(ast, dict):
        logger.critical('Expecting AST as a dictionary, got {} instead.', ast)
        exit(10)

    # Get the only key
    key = next(iter(ast))

    # substitute children
    if isinstance(ast[key], list):
        for i, element in enumerate(ast[key]):
            ast[key][i] = substituteAST(element)
    elif isinstance(ast[key], str) or isinstance(ast[key], dict):
        ast[key] = substituteAST(ast[key])
    else:
        logger.critical('AST includes an unknown type. Got {}.', ast[key])
        exit(11)
    return ast

def parseEquation(text):
    # Parse things from the shell, these can be assignments to
    # variables, or conditions of if and while.
    # TODO: add string parsing
    # FIXME: Using paranthesis makes this hang!
    # FIXME: Fix the speed of this pyparsing crap
    function = parser.parseString(text)[0]
    if not isinstance(function, str):
        function = function.asList()
    logger.debug('Parsed function: {}', function)
    ast = buildAST(function)
    logger.debug('Built AST.')
    printAST(ast)
    ast = substituteAST(ast)
    logger.debug('Substituted AST.')
    printAST(ast)
    return ast

def evaluateEquation(ast):
    # Eval can be dangerous, so we do this by hand
    if isinstance(ast, int) or isinstance(ast, float):
        return ast

    if not isinstance(ast, dict):
        logger.critical('Expecting AST as a dictionary, got {} instead.', ast)
        exit(12)

    # Get the only key
    key = next(iter(ast))

    if isinstance(ast[key], list):
        # Calculate children
        for i, element in enumerate(ast[key]):
            if isinstance(element, dict):
                ast[key][i] = evaluateEquation(element)
        # This is a binary operand with potentially more than 
        # 2 operands. Respect Associativity
        if key in right_binary_operators:
            value = ast[key][-1]
            for element in reversed(ast[key][0:-2]):
                value = left_binary_operators[key](element, value)
            return value
        elif key in left_binary_operators:
            value = ast[key][0]
            for element in ast[key][1:]:
                value = left_binary_operators[key](value, element)
            return value
        else:
            logger.critical('AST includes an unknown binary operand {}.', key)
            exit(13)
    elif isinstance(ast[key], int) or isinstance(ast[key], float) or isinstance(ast[key], dict):
        ast[key] = evaluateEquation(ast[key])
        # This is a unary operand, NOT or NEG
        if key in unary_operators:
            return unary_operators[key](ast[key])
        else:
            logger.critical('AST includes an unknown unary operand {}.', key)
            exit(14)
    else:
        logger.critical('AST includes an unknown type. Got {}.', ast[key])
        exit(15)
