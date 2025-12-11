"""Starts the MySQL server"""

import os
import subprocess
import pathlib

PORT = 11211
DEFAULT_BUILD_TYPE = "debug"
DEFAULT_DATADIR = f"{os.getcwd()}/mydata"
DEFAULT_USER = "root"
DEFAULT_DATABASE = "mysql"
SOCKET = "/tmp/mysql-8.0.sock"


def get_socket_name(version, args):
    """Generates a socket file name from the version an build type."""
    return f"/tmp/mysql-{version['MYSQL_VERSION_MAJOR']}.{version['MYSQL_VERSION_MINOR']}.sock"


def read_mysql_version(version_file_name="MYSQL_VERSION"):
    """Parses the version file to a dict."""
    version = {}
    with open(version_file_name, "r", encoding="ascii") as version_file:
        for line in version_file:
            data = line.split("=")
            value = data[1].strip()
            version[data[0]] = int(value) if value.isdigit() else value
    return version


def get_mysqld_executable_path(version, build_dir):
    """The full executable path of mysqld given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/sql/mysqld"
    return f"{build_dir}/runtime_output_directory/mysqld"


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


def start_client(executable, args, unknown_args):
    """Starts the MySQL client"""

    subprocess_args = [executable] + deparse_arglist(args) + unknown_args

    print(f"Running mysql like this: {" ".join(subprocess_args)}")

    subprocess.call(subprocess_args)
