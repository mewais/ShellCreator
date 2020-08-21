#!/usr/bin/python3

import os
from prompt_toolkit.completion import NestedCompleter, PathCompleter

nested_dict = {}

def updateCompleter(name, cls):
    global nested_dict
    if cls.word_completer and cls.file_completer:
        logger.critical('A command can have either a word autocompleter or a file autocompleter. Not both.')
        exit(15)
    elif cls.word_completer:
        nested_dict[name] = cls.word_completer
    elif cls.file_completer:
        extensions = cls.file_completer
        # Filter Function
        def fileFilter(filename, extensions=extensions):
            for extension in extensions:
                if filename.endswith('.' + extension):
                    return True
                elif os.path.isdir(filename):
                    return True
            return False
        nested_dict[name] = PathCompleter(file_filter=fileFilter)
    else:
        nested_dict[name] = None
    return NestedCompleter.from_nested_dict(nested_dict)
