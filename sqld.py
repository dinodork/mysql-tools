"""Starts the MySQL server"""

import argparse
import os
import pathlib
import sys

import mysql


class ExpandPath(argparse.Action):
    """Because mysqld has this annoying habit of not expanding ~"""

    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, option_string.replace("--", ""), values.expanduser())


def main():
    """Guts of the script"""

    parser = argparse.ArgumentParser(description="Starts mysqld in the background.")

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
        action=ExpandPath,
        help="passed to mysqld, but expands the `~' character",
    )

    build_args = parser.add_mutually_exclusive_group()
    build_args.add_argument(
        "-B",
        "--build-dir",
        help="lets you specify the build directory directly, instead of inferring it from the "
        "build type (see --build-type)",
    )
    build_args.add_argument(
        "-b",
        "--build-type",
        help="assumes that you have built mysql in a directory named "
        "`build/<build type>` in the current directory. You can specify an "
        "arbitrary build directory using --build-dir",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="don't actually start mysqld, only print how it would have started and then exit",
    )

    parser.add_argument("-C", help="change to DIR before doing anything else")

    args, unknown_args = parser.parse_known_args()

    workdir = args.C if args.C else os.getcwd()
    datadir = args.datadir if args.datadir else f"{workdir}/{mysql.DEFAULT_DATADIR}"

    os.makedirs(datadir, exist_ok=True)

    if args.build_dir:
        build_dir = args.build_dir
    else:
        build_dir = f"{workdir}/build/{args.build_type}"

    if not args.build_dir and not args.build_type:
        setattr(args, "build_type", "debug")
        build_type = "debug"
    elif args.build_type:
        build_type = args.build_type

    # pylint: disable=duplicate-code
    try:
        version = mysql.read_mysql_version(workdir)
    except OSError:
        print("Exiting")
        sys.exit(1)

    mysqld_executable = mysql.get_mysqld_executable_path(version, build_dir)

    if args.socket is None:
        args.socket = mysql.get_socket_name(version, args)

    # Remove all arguments that were meant only for this script
    del args.build_dir
    del args.build_type
    del args.C
    del args.datadir

    if version["MYSQL_VERSION_MAJOR"] <= 5:
        unknown_args.append(f"--lc-messages-dir={build_dir}/sql/share/english")

    if build_type.lower() == "debug":
        unknown_args.append("--gdb")

    unknown_args.append(f"--datadir={datadir}")

    mysql.start_mysqld(mysqld_executable, args, unknown_args)


if __name__ == "__main__":
    main()
