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


def make_parser():
    """Sets up the complete commandline parser"""

    parser = argparse.ArgumentParser(description="Starts mysqld in the background.")

    mysqld_args = parser.add_argument_group(
        "mysqld options", "Passed verbatim to mysqld."
    )

    # All arguments added here must be manually added to mysqld_args
    mysqld_args.add_argument(
        "--datadir",
        type=pathlib.Path,
        action=ExpandPath,
        help="passed to mysqld, but expands the `~' character",
    )
    mysqld_args.add_argument(
        "--lower-case-table-names",
        type=int,
        default=mysql.Defaults.LOWER_CASE_TABLE_NAMES,
    )
    mysqld_args.add_argument("--no-defaults", action="store_true")
    mysqld_args.add_argument("--port", type=int, default=mysql.Defaults.PORT)
    mysqld_args.add_argument("--socket", type=str)

    build_specific_args = parser.add_mutually_exclusive_group()
    build_specific_args.add_argument(
        "-B",
        "--build-dir",
        help="lets you specify the build directory directly, instead of inferring it from the "
        "build type (see --build-type)",
    )
    build_specific_args.add_argument(
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

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="debug this script",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="verbose",
    )

    parser.add_argument(
        "-C",
        metavar="directory",
        help="change to <directory> before doing anything else",
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Answer every question with 'yes'",
    )

    parser.add_argument(
        "--create",
        action="store_true",
        help="Creates a database before starting.",
    )

    return parser


def main():
    """Guts of the script"""

    parser = make_parser()

    args, unknown_args = parser.parse_known_args()

    workdir = args.C if args.C else os.getcwd()
    datadir = args.datadir if args.datadir else f"{workdir}/{mysql.Defaults.DATADIR}"

    os.makedirs(datadir, exist_ok=True)

    try:
        version = mysql.read_mysql_version(args, workdir)
    except OSError:
        print("Exiting")
        sys.exit(1)

    build_type, build_dir = mysql.determine_build_specifics(args)

    mysqld_argv = (
        [
            f"--datadir={datadir}",
            f"--lower_case_table_names={args.lower_case_table_names}",
            f"--port={args.port}",
        ]
        + (["--no-defaults"] if args.no_defaults else [])
        + unknown_args
    )

    socket = mysql.get_socket_path(version, build_type)

    if not args.socket:
        mysqld_argv += [f"--socket={socket}"]

    if build_type.lower() == "debug":
        mysqld_argv += ["--gdb"]

    mysqld_executable = mysql.get_mysqld_executable_path(version, build_dir)

    if version["MYSQL_VERSION_MAJOR"] <= 5:
        unknown_args.append(f"--lc-messages-dir={build_dir}/sql/share/english")

    lockfile = f"{socket}.lock"
    if os.path.isfile(lockfile):
        if args.yes:
            os.remove(lockfile)
        else:
            answer = input(f"Found lock file {lockfile}. Delete? [y/n/Q]: ")
            if answer.lower().strip() == "y":
                os.remove(lockfile)
            elif answer.lower().strip() == "q" or answer == "":
                sys.exit(0)

    if args.create:
        mysql.create_database(version, mysqld_executable, datadir, workdir, args)

    mysql.start_mysqld(mysqld_executable, args, mysqld_argv)


if __name__ == "__main__":
    main()
