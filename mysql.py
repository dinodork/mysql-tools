"""Starts the MySQL server"""

import os
import sys
import subprocess
import pathlib

PORT = 11211
DEFAULT_BUILD_TYPE = "debug"
DEFAULT_DATADIR = f"{os.getcwd()}/mydata"
DEFAULT_USER = "root"
DEFAULT_DATABASE = "test"
SOCKET = "/tmp/mysql-8.0.sock"


def deparse(flag, arg):
    """Deparses a single command-line argument"""
    deparsed_flag = f"--{flag}" if len(flag) > 1 else f"-{flag}"

    if isinstance(arg, bool):
        return deparsed_flag if arg else None

    if isinstance(arg, str):
        # Black can't handle this line
        # fmt:off
        return f"{deparsed_flag}={str(arg).strip('\'')}"
        # fmt:on
    if isinstance(arg, int):
        return f"{deparsed_flag}={int(arg)}"

    if isinstance(arg, pathlib.Path):
        return f"{deparsed_flag}={arg}"

    return None


def deparse_arglist(args):
    """Deparses an argparse Namespace into a list of command-line arguments"""
    arglist = []

    for item in vars(args).items():
        deparsed_item = deparse(*item)
        if deparsed_item:
            arglist.append(deparsed_item)

    return arglist


def start_mysqld(executable, args, unknown_args):
    """Guts of the script"""

    subprocess_args = [executable] + deparse_arglist(args) + unknown_args

    print(f"Running mysqld like this: {" ".join(subprocess_args)}")

    # pylint: disable=consider-using-with
    subprocess.Popen(subprocess_args)


def start_client(executable, args):
    """Starts the MySQL client"""

    subprocess_args = [executable] + deparse_arglist(args) + sys.argv[1:]

    print(f"Running mysql like this: {" ".join(subprocess_args)}")

    subprocess.call(subprocess_args)
