#!/usr/bin/python3

import pyparsing
import logging
import operator

from .Utils.Operators import operator_and, operator_or

logger = logging.getLogger('Shell')

variable_name = pyparsing.Combine(pyparsing.Literal('$') + pyparsing.Word(pyparsing.alphas, pyparsing.alphanums + '_'))
integer = pyparsing.pyparsing_common.signed_integer
double = pyparsing.pyparsing_common.real
true = pyparsing.Keyword('True')
false = pyparsing.Keyword('False')
string = pyparsing.QuotedString('\'', escChar='\\') | pyparsing.QuotedString('\"', escChar='\\')
parser = pyparsing.operatorPrecedence(variable_name | double | integer | string | 
                                true | false, [
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

def parseExpression(text):
    # Parse things from the shell, these can be assignments to
    # variables, or conditions of if and while.
    # TODO: add string parsing
    function = parser.parseString(text)[0]
    if not isinstance(function, str) and not isinstance(function, int) and not isinstance(function, float):
        function = function.asList()
    logger.debug('Parsed function: {}', function)
    return function

def evaluateExpression(ast, builtin_variables, variables):
    def evaluateString(string):
        if string[0] == '$':
            if string[1:] in builtin_variables:
                value = builtin_variables[string[1:]]
            elif string[1:] in variables:
                value = variables[string[1:]]
            else:
                logger.error('Variable {} does not exist.', string[1:])
                raise NameError('Variable does not exist')
        elif string == 'True':
            value = True
        elif string == 'False':
            value = False
        else:
            value = string
        return value
    # Eval can be dangerous, so we do this by hand
    if isinstance(ast, str):
        # This should only happen on the top level
        return evaluateString(ast)
    if isinstance(ast, int) or isinstance(ast, float):
        return ast

    if not isinstance(ast, list):
        logger.critical('Expecting AST as a list, got {} instead.', ast)
        exit(5)

    if len(ast) == 2:
        value = evaluateExpression(ast[1], builtin_variables, variables)
        value = unary_operators[ast[0]](value)
        return value
    elif ast[1] in right_binary_operators:
        value = evaluateExpression(ast[-1], builtin_variables, variables)
        for i in range(len(ast)-2, -1, -2):
            tmp_value = evaluateExpression(ast[i-1], builtin_variables, variables)
            value = right_binary_operators[ast[i]](tmp_value, value)
        return value
    elif ast[1] in left_binary_operators:
        value = evaluateExpression(ast[0], builtin_variables, variables)
        for i in range(1, len(ast), 2):
            tmp_value = evaluateExpression(ast[i+1], builtin_variables, variables)
            value = left_binary_operators[ast[i]](value, tmp_value)
        return value
    else:
        logger.critical('AST includes an unknown binary operand {}.', key)
        exit(6)
