#!/usr/bin/python3

from prompt_toolkit.application import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

@Condition
def shouldIndent():
    document = get_app().current_buffer.document
    line = document.current_line_before_cursor
    if not line or line.isspace():
        # If this is the first character or
        # If all what's before is whitespaces
        # indent
        return True
    else:
        # Otherwise, it's autocompletion
        return False

@bindings.add('tab', filter=shouldIndent)
def _(event):
    event.app.current_buffer.insert_text('    ')
