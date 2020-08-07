# Shell Creator
This is a simple python library that can be used to create entire shells for CLI applications. It was originally a part of another application, and then I decided to split it and make it a library on its own. The shell has following features:
- Python like arithmetic operators
- Setting/Unsetting variables
- Builtin commands for variable manipulation
- Builtin support for if statements and while loops (not yet implemented)
- Easily extensible with new commands through simple class inheritance
- Colorful, with nice logging

## How to use
### Help and Exiting
use the following commands to get help and exit:
- `help --commands` will give you the list of all commands in the shell
- `help --variables` will give you the list of all variables in the shell
- `exit` to exit the shell

### Data Types
The supported types are the same basic types of python. Those are:
- Integers
- Floats
- Booleans (True or False)
- Strings (single and double quoted, escaped by /)

### Operators
The shell uses the same python arithmetic operators for convenience, it also maintains their precedence and associativity. The operators are:
| Operator             | Description                                       |
|----------------------|---------------------------------------------------|
| **                   | Exponent                                          |
| -x                   | Unary minus                                       |
| *, /, //, %          | Multiplication, Division, Floor division, Modulus |
| +, -                 | Addition, Subtraction                             |
| ==, !=, >, >=, <, <= | Comparisons                                       |
| not                  | Logical NOT                                       |
| and                  | Logical AND                                       |
| or                   | Logical OR                                        |

**WARNING:** Chaining comparison arguments will have a different effect from python. The shell will parse them one by one, in other words: `a < b > c` will be parsed as `(a < b) > c` rather than `a < b and b > c`

### Variables
The shell can handle saving, deleting, and accessing variables in the following ways:

```bash
echo $var
set var=$var2 + 485 * 12
unset $var
```
When dealing with variables pay attention to the following points:
- Reading a shell variable must precede its name with a `$`.
- Writing to a variable must NOT precede its name with a `$`.
- Setting an existing variable will overwrite its existing value.
- Unsetting or Echoing a non-existent variable will generate an error.

There are builtin variables, those are variables that can be set to and modified, but never unset. A library user can choose to add those as needed by using the function call `shell.addBuiltinVariable`

### If and While
The shell supports if conditions and while loops, the syntax is as follows:
```
if $var1
  command
  command
elif $var2 > 50
  command
else
  command
  command
end

while $var3 + 40 < $var4
  command
end
```

### Adding commands
The Shell Creator utilizes the great [docopt](http://docopt.org/) library to build the commands of the shell (including the builtin ones). There's a base `Command` class that must be inherited and overridden to implement new commands. Example:
```python
class ReadFile(Command):
  usage='''
  read_file

  Usage:
      read_file -h
      read_file [--f FORMAT] FILE

  Options:
      -h, --help                    Print this help message
      -f FORMAT, --format=FORMAT    The format of the file to read
  '''

  def action(self):
      print(self.args)
      print(self.args['FORMAT'])
      print(self.args['FILE'])

  shell.addCommand('read_file', ReadFile)
```

### Styling and Logging
The shell uses `logging` for logging, with the namespace `SHELL`. It utilizes [this formatter](https://github.com/davidohana/colargulog) to better format and colorize logging. It also uses `prompt_toolkit`'s styling to style the prompt itself. You can refer to the examples or to `prompt_toolkit`'s documentation for more details

The logging format is as follows: `self.logger.error('A logging message {}', value)` where self refers to the command class you create.

## Prerequisites and Installation
You can install by simply running `pip3 install ShellCreator`

The library depends on the following libraries:
- Pygments
- prompt_toolkit
- docopt
- pyparsing
