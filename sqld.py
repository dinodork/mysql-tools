"""Starts the MySQL server"""

import argparse
import logging
import os
import pathlib
import signal
import sys

import mysql


class _Verbosity(argparse.Action):
    """Keeps a single integer: -v adds 1, -q subtracts 1."""

    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest)
        setattr(namespace, self.dest, current + self.const)


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
        action=_Verbosity,
        nargs=0,
        const=1,
        default=1,
        dest="verbose",
        help="increase verbosity (repeatable)",
    )

    parser.add_argument(
        "-q",
        action=_Verbosity,
        nargs=0,
        const=-1,
        dest="verbose",
        help="decrease verbosity (repeatable)",
    )

    parser.add_argument(
        "-C",
        "--workdir",
        default=os.getcwd(),
        help="change to DIR before doing anything else",
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

    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stops this mysqld.",
    )

    parser.add_argument(
        "--get-pid",
        action="store_true",
        help="Prints this mysqld's pid .",
    )

    return parser


def main():
    """Guts of the script"""

    parser = make_parser()

    args, mysqld_args = parser.parse_known_args()

    mysql.setup_logging(args.verbose)

    if args.datadir:
        if os.path.isabs(args.datadir):
            datadir = args.datadir
        else:
            datadir = os.path.abspath(f"{args.datadir}")
    else:
        datadir = f"{args.workdir}/{mysql.Defaults.DATADIR}"

    if not os.path.isabs(datadir):
        datadir = os.path.abspath(datadir)

    os.makedirs(datadir, exist_ok=True)

    build_type, build_dir = mysql.determine_build_specifics(args)

    logging.debug("Build type: %s", build_type)
    logging.debug("Build dir: %s", build_dir)

    try:
        version = mysql.read_version(args.workdir)
    except OSError:
        logging.info("Exiting")
        sys.exit(1)

    bindir = mysql.get_bin_dir(version, build_dir)

    server = mysql.Server(datadir, version, bindir, args.verbose)

    mysqld_executable_path = mysql.get_mysqld_executable_path(version, build_dir)

    if args.get_pid:
        pid = server.get_pid()
        if pid is None:
            logging.critical("Failed to find running mysqld", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.stop:
        pid = server.get_pid()
        if pid is None:
            logging.critical("Failed to find running mysqld")
            sys.exit(1)

        logging.debug("Killing mysql with pid %s", pid)

        os.kill(pid, signal.SIGTERM)
        sys.exit(0)

    mysqld_args += [
        f"--datadir={datadir}",
        f"--lower_case_table_names={args.lower_case_table_names}",
        f"--port={args.port}",
    ]

    if args.no_defaults:
        mysqld_args += ["--no-defaults"]

    socket = args.socket if args.socket else mysql.get_socket_path(version, build_type)

    mysqld_args += [f"--socket={socket}"]

    if build_type and build_type.lower() == "debug":
        mysqld_args += ["--gdb"]

    if version["MYSQL_VERSION_MAJOR"] <= 5:
        mysqld_args += [f"--lc-messages-dir={build_dir}/sql/share/english"]

    lockfile = f"{socket}.lock"
    if not args.dry_run and os.path.isfile(lockfile):
        if args.yes:
            os.remove(lockfile)
        else:
            answer = input(f"Found lock file {lockfile}. Delete? [y/n/Q]: ")
            if answer.lower().strip() == "y":
                os.remove(lockfile)
            elif answer.lower().strip() == "q" or answer == "":
                sys.exit(0)

    if args.create:
        server.create_database(args, mysqld_args)

    logging.info("start_mysqld(%s, %s, %s)", mysqld_executable_path, args, mysqld_args)
    server.start(args, mysqld_args)


if __name__ == "__main__":
    main()
