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


### If and While
TODO

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

  @classmethod
  def action(cls):
      print(cls.args)
      print(cls.args['FORMAT'])
      print(cls.args['FILE'])

  addCommand('read_file', ReadFile)
```

### Styling
The shell uses `logging` for logging, with the namespace `SHELL`. It utilizes [this formatter](https://github.com/davidohana/colargulog) to better format and colorize logging. It also uses `prompt_toolkit`'s styling to style the prompt itself. You can refer to the examples or to `prompt_toolkit`'s documentation for more details

## Prerequisites and Installation
TODO
