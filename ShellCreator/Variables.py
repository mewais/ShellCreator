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
                                (pyparsing.oneOf('* / // %'), 2, pyparsing.opAssoc.LEFT),
                                (pyparsing.oneOf('+ -'), 2, pyparsing.opAssoc.LEFT),
                                (pyparsing.oneOf('> >= < <= == !='), 2, pyparsing.opAssoc.LEFT),
                                ('not', 1, pyparsing.opAssoc.RIGHT),
                                ('and', 2, pyparsing.opAssoc.LEFT),
                                ('or', 2, pyparsing.opAssoc.LEFT)])
unary_operators = {
    '-': operator.neg,
    'not': operator.not_,
}
right_binary_operators = {
    '**': operator.pow
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

def parseEquation(text):
    # Parse things from the shell, these can be assignments to
    # variables, or conditions of if and while.
    # TODO: add string parsing
    function = parser.parseString(text)[0]
    if not isinstance(function, str):
        function = function.asList()
    logger.debug('Parsed function: {}', function)
    return function

def evaluateEquation(ast):
    def evaluateString(string):
        if string[0] == '$':
            if string[1:] in variables:
                value = variables[string[1:]]
            else:
                logger.error('Variable {} does not exist.', string[1:])
                raise NameError('Variable does not exist')
        else:
            try:
                value = stringToNumber(string)
            except ValueError as e:
                logger.critical('All strings must be variables or number literals. Got {}', string)
                exit(4)
        return value
    # Eval can be dangerous, so we do this by hand
    if isinstance(ast, str):
        # This should only happen on the top level
        return evaluateString(ast)

    if not isinstance(ast, list):
        logger.critical('Expecting AST as a list, got {} instead.', ast)
        exit(5)

    if len(ast) == 2:
        value = evaluateEquation(ast[1])
        value = unary_operators[ast[0]](value)
        return value
    elif ast[1] in right_binary_operators:
        value = evaluateEquation(ast[-1])
        for i in range(len(ast)-2, -1, -2):
            value = right_binary_operators[ast[i]](evaluateEquation(ast[i-1]), value)
        return value
    elif ast[1] in left_binary_operators:
        value = evaluateEquation(ast[0])
        for i in range(1, len(ast), 2):
            value = left_binary_operators[ast[i]](value, evaluateEquation(ast[i+1]))
        return value
    else:
        logger.critical('AST includes an unknown binary operand {}.', key)
        exit(6)
