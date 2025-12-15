"""Starts the MySQL server"""

import subprocess
import pathlib
import sys

PORT = 11211
DEFAULT_BUILD_TYPE = "debug"
DEFAULT_DATADIR = "mydata"
DEFAULT_USER = "root"
DEFAULT_DATABASE = "mysql"
SOCKET = "/tmp/mysql-8.0.sock"


# pylint: disable=inconsistent-return-statements
def get_build_type(args):
    # pylint: enable=inconsistent-return-statements
    """Determines the type of the build."""

    if args.build_type:
        return args.build_type
    if args.build_dir:
        build_dir = args.build_dir
        cmake_cache_path = f"{build_dir}/CMakeCache.txt"
        try:
            with open(cmake_cache_path, "r", encoding="utf-8") as cmake_cache:
                for line in cmake_cache:
                    if line[:24] == "CMAKE_BUILD_TYPE:STRING=":
                        print(f" lajn '{line[24:]}'")
                        return line[24:].strip()
        except FileNotFoundError:
            print(f"Warning, can't find {cmake_cache_path}", file=sys.stderr)

            return "unknown"


def get_socket_name(version, args):
    """Generates a socket file name from the version an build type."""
    return (
        f"/tmp/mysql-{version['MYSQL_VERSION_MAJOR']}.{version['MYSQL_VERSION_MINOR']}-"
        f"{get_build_type(args)}.sock"
    )


def read_mysql_version(workdir, version_file_name="MYSQL_VERSION"):
    """Parses the version file to a dict."""
    version = {}
    try:
        with open(
            f"{workdir}/{version_file_name}", "r", encoding="ascii"
        ) as version_file:
            for line in version_file:
                data = line.split("=")
                value = data[1].strip()
                version[data[0]] = int(value) if value.isdigit() else value
    except FileNotFoundError:
        print(
            f"Warning, can't find {version_file_name} in {workdir}!",
            file=sys.stderr,
        )
        raise
    return version


def get_mysqld_executable_path(version, build_dir):
    """The full executable path of mysqld given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/sql/mysqld"
    return f"{build_dir}/runtime_output_directory/mysqld"


def get_mysql_executable_path(version, build_dir):
    """The full executable path of mysqld given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/client/mysql"
    return f"{build_dir}/runtime_output_directory/mysql"


def deparse(flag, arg):
    """Deparses a single command-line argument"""
    deparsed_flag = f"--{flag}" if len(flag) > 1 else f"-{flag}"

    if isinstance(arg, bool):
        return deparsed_flag if arg else None

    if isinstance(arg, str):
        return f"{deparsed_flag}={str(arg)}"

    if isinstance(arg, int):
        return f"{deparsed_flag}={int(arg)}"

    if isinstance(arg, pathlib.Path):
        return f"{deparsed_flag}={arg}"

    return None


def deparse_arglist(args):
    """Deparses an argparse Namespace back into a list of command-line arguments."""
    arglist = []

    for item in vars(args).items():
        deparsed_item = deparse(*item)
        if deparsed_item:
            arglist.append(deparsed_item)

    return arglist


def start_mysqld(executable, args, unknown_args):
    """Starts the mysqld process."""

    subprocess_args = [executable] + deparse_arglist(args) + unknown_args

    print(f"Running mysqld like this: {" ".join(subprocess_args)}")

    if args.dry_run:
        return

    # pylint: disable=consider-using-with
    subprocess.Popen(subprocess_args)


def start_client(executable, args, unknown_args):
    """Starts the MySQL client."""

    subprocess_args = [executable] + deparse_arglist(args) + unknown_args

    print(f"Running mysql like this: {" ".join(subprocess_args)}")

    subprocess.call(subprocess_args)
