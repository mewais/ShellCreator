#!/usr/bin/python3

import os
from prompt_toolkit.application import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter, NestedCompleter, PathCompleter, DynamicCompleter

class Completer():

    def __init__(self):
        self.variables = []
        self.quoted_variables = []
        self.nested_dict = {}

    def getCompleter(self):
        # document = get_app().current_buffer.document
        nested_completer = NestedCompleter.from_nested_dict(self.nested_dict)
        variable_completer = WordCompleter(self.variables)
        quoted_variable_completer = WordCompleter(self.quoted_variables)
        def selector():
            document = get_app().current_buffer.document
            if document.char_before_cursor == '$':
                return variable_completer
            elif document.current_line_before_cursor.endswith('${'):
                return quoted_variable_completer
            else:
                return nested_completer
        # return DynamicCompleter(lambda: variable_completer if document.char_before_cursor == '$' or document.current_line_before_cursor.endswith('${') else nested_completer)
        return DynamicCompleter(selector)

    def addVariable(self, name):
        if ('$' + name) in self.variables:
            logger.critical('Name {} already exists in variable autocompletion.', name)
            exit(16)
        if ('${' + name + '}') in self.quoted_variables:
            logger.critical('Name {} already exists in variable autocompletion.', name)
            exit(16)
        self.variables.append('$' + name)
        self.quoted_variables.append('${' + name + '}')

    def deleteVariable(self, name):
        if ('$' + name) not in self.variables:
            logger.critical('Name {} already does not exist in variable autocompletion.', name)
            exit(17)
        if ('${' + name + '}') not in self.quoted_variables:
            logger.critical('Name {} already does not exist in variable autocompletion.', name)
            exit(17)
        self.variables.remove('$' + name)
        self.quoted_variables.remove('${' + name + '}')

    def addCommand(self, name, cls):
        if cls.word_completer and cls.file_completer:
            logger.critical('A command can have either a word autocompleter or a file autocompleter. Not both.')
            exit(15)
        elif cls.word_completer:
            self.nested_dict[name] = cls.word_completer
        elif cls.file_completer:
            extensions = cls.file_completer
            # Filter Filename Function
            def fileFilter(filename, extensions=extensions):
                for extension in extensions:
                    if filename.endswith('.' + extension):
                        return True
                    elif os.path.isdir(filename):
                        return True
                return False
            self.nested_dict[name] = PathCompleter(file_filter=fileFilter)
        else:
            self.nested_dict[name] = None
