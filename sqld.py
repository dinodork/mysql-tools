"""Starts the MySQL server"""

import argparse
import os
import pathlib

import mysql


class ExpandPath(argparse.Action):
    """Because mysqld has this annoying habit of not expanding ~"""

    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, option_string.replace("--", ""), values.expanduser())


def main():
    """Guts of the script"""

    parser = argparse.ArgumentParser(description="Starts mysqld and drops you into it.")

    mysqld_args = parser.add_argument_group(
        "mysqld options", "Passed verbatim to mysqld."
    )

    mysqld_args.add_argument("--port", type=int, default=mysql.PORT)
    mysqld_args.add_argument("--socket", type=str)
    mysqld_args.add_argument("--no-defaults", action="store_true")
    mysqld_args.add_argument("--lower-case-table-names", type=int, default=1)
    mysqld_args.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=mysql.DEFAULT_DATADIR,
        action=ExpandPath,
        help="Passed to mysqld, but expands the `~' character.",
    )

    parser.add_argument(
        "-B",
        "--build-dir",
        type=ascii,
        help="Lets you specify the build " "directory directly.",
    )
    parser.add_argument(
        "-b",
        "--build-type",
        type=ascii,
        default=mysql.DEFAULT_BUILD_TYPE,
        help="This option assumes that you have built mysql in a directory named "
        "`build/<build type>` in the current directory. You can specify an "
        "arbitrary build directory using --build-dir.",
    )

    args, unknown_args = parser.parse_known_args()

    os.makedirs(args.datadir, exist_ok=True)

    if args.build_dir:
        build_dir = args.build_dir.strip("'")
    else:
        # Black can't handle this line
        # fmt:off
        build_dir = f"build/{args.build_type.strip('\'')}"
        # fmt:on

    # Remove all arguments that were meant only for this script
    del args.build_dir
    del args.build_type

    version = mysql.read_mysql_version()
    mysqld_executable = mysql.get_mysqld_executable_path(version, build_dir)

    if args.socket is None:
        args.socket = mysql.get_socket_name(version, args)

    mysql.start_mysqld(mysqld_executable, args, unknown_args)


if __name__ == "__main__":
    main()
